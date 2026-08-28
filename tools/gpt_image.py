#!/usr/bin/env python3
"""Generate project PNG assets with OpenAI GPT Image 2.

This is the executable bridge used when Codex CLI does not expose the built-in
image-generation tool. The web-service worker injects the signed-in user's API
key as OPENAI_API_KEY for the lifetime of the Codex child process.

Examples:
  python3 tools/gpt_image.py probe
  python3 tools/gpt_image.py generate \
    --prompt-file design/prompts/sprite_compass.txt \
    --out assets/images/sprites/sprite_compass.png \
    --size 1024x1024 \
    --quality high
  python3 tools/gpt_image.py edit \
    --prompt-file design/prompts/keyart-integration.txt \
    --image art/keyart-draft.png \
    --image assets/images/sprites/sprite_eagle.png \
    --out art/keyart-integrated.png \
    --size 1536x1024 --fidelity high
"""

from __future__ import annotations

import argparse
import base64
import json
import mimetypes
import os
import re
import secrets
import struct
import sys
import tempfile
import time
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any


API_ROOT = "https://api.openai.com/v1"
MODEL = "gpt-image-2"
PNG_SIGNATURE = b"\x89PNG\r\n\x1a\n"
RETRYABLE_HTTP_STATUS = {408, 409, 429, 500, 502, 503, 504}
MAX_PROMPT_CHARS = 32_000
# The Images API's own ceiling for reference images on one edit call.
MAX_INPUT_IMAGES = 16
MAX_INPUT_BYTES = 50 * 1024 * 1024


class ImageGenerationError(RuntimeError):
    """A safe-to-display image generation failure."""


def _api_key() -> str:
    key = os.environ.get("OPENAI_API_KEY", "").strip()
    if not key:
        raise ImageGenerationError(
            "OPENAI_API_KEY is not set. In flutter-game-web-service it must be "
            "injected automatically from the signed-in user's saved API key."
        )
    return key


def _validate_size(value: str) -> str:
    if value == "auto":
        return value
    match = re.fullmatch(r"(\d+)x(\d+)", value)
    if not match:
        raise argparse.ArgumentTypeError("size must be auto or WIDTHxHEIGHT")
    width, height = (int(part) for part in match.groups())
    short_edge, long_edge = sorted((width, height))
    pixels = width * height
    if width % 16 or height % 16:
        raise argparse.ArgumentTypeError("both size edges must be multiples of 16")
    if long_edge > 3840:
        raise argparse.ArgumentTypeError("maximum size edge is 3840px")
    if long_edge > short_edge * 3:
        raise argparse.ArgumentTypeError("long-to-short edge ratio must not exceed 3:1")
    if not 655_360 <= pixels <= 8_294_400:
        raise argparse.ArgumentTypeError(
            "total pixels must be between 655,360 and 8,294,400"
        )
    return value


def _read_prompt(args: argparse.Namespace) -> str:
    if args.prompt_file:
        try:
            prompt = Path(args.prompt_file).read_text(encoding="utf-8")
        except OSError as exc:
            raise ImageGenerationError(
                f"cannot read prompt file {args.prompt_file}: {exc}"
            ) from exc
    else:
        prompt = args.prompt
    prompt = (prompt or "").strip()
    if not prompt:
        raise ImageGenerationError("prompt is empty")
    if len(prompt) > MAX_PROMPT_CHARS:
        raise ImageGenerationError(
            f"prompt is too long ({len(prompt)} chars; max {MAX_PROMPT_CHARS})"
        )
    return prompt


def _error_message(status: int, body: bytes) -> str:
    text = body.decode("utf-8", errors="replace")
    try:
        payload = json.loads(text)
        error = payload.get("error", payload)
        if isinstance(error, dict):
            message = str(error.get("message", error))
            code = error.get("code") or error.get("type")
            suffix = f" ({code})" if code else ""
            return f"OpenAI Images API HTTP {status}: {message}{suffix}"
    except (json.JSONDecodeError, AttributeError):
        pass
    compact = " ".join(text.split())[:1000]
    return f"OpenAI Images API HTTP {status}: {compact or 'empty error response'}"


def _request_json(
    method: str,
    endpoint: str,
    *,
    payload: dict[str, Any] | None = None,
    timeout: int,
    max_attempts: int,
) -> tuple[dict[str, Any], str | None]:
    data = None if payload is None else json.dumps(payload).encode("utf-8")
    headers = {
        "Authorization": f"Bearer {_api_key()}",
        "User-Agent": "flutter-gambling-studio-gpt-image/1.0",
    }
    if data is not None:
        headers["Content-Type"] = "application/json"

    for attempt in range(1, max_attempts + 1):
        request = urllib.request.Request(
            f"{API_ROOT}{endpoint}",
            data=data,
            headers=headers,
            method=method,
        )
        try:
            with urllib.request.urlopen(request, timeout=timeout) as response:
                body = response.read()
                request_id = response.headers.get("x-request-id")
                try:
                    decoded = json.loads(body)
                except json.JSONDecodeError as exc:
                    raise ImageGenerationError(
                        "OpenAI Images API returned invalid JSON"
                    ) from exc
                if not isinstance(decoded, dict):
                    raise ImageGenerationError(
                        "OpenAI Images API returned an unexpected JSON value"
                    )
                return decoded, request_id
        except urllib.error.HTTPError as exc:
            body = exc.read()
            if exc.code in RETRYABLE_HTTP_STATUS and attempt < max_attempts:
                retry_after = exc.headers.get("Retry-After")
                try:
                    delay = min(30.0, max(1.0, float(retry_after or 2**attempt)))
                except ValueError:
                    delay = float(2**attempt)
                print(
                    f"retryable OpenAI HTTP {exc.code}; retrying in {delay:g}s "
                    f"({attempt}/{max_attempts})",
                    file=sys.stderr,
                )
                time.sleep(delay)
                continue
            raise ImageGenerationError(_error_message(exc.code, body)) from exc
        except urllib.error.URLError as exc:
            # A timeout or dropped connection can be ambiguous: retrying could
            # create and bill a duplicate image, so leave that choice to Codex.
            raise ImageGenerationError(
                f"OpenAI Images API network error: {exc.reason}"
            ) from exc

    raise ImageGenerationError("OpenAI Images API request exhausted all attempts")


def _read_input_images(paths: list[str]) -> list[tuple[str, str, bytes]]:
    """Load the reference images an edit call is built from.

    These are the whole point of `edit`: the model is not told *about* the
    game's hero and symbols, it is handed the shipped files and asked to render
    those objects into the scene. Describing them produces something similar;
    passing them produces the same objects.
    """
    if not paths:
        raise ImageGenerationError("edit needs at least one --image")
    if len(paths) > MAX_INPUT_IMAGES:
        raise ImageGenerationError(
            f"{len(paths)} reference images; the API accepts at most {MAX_INPUT_IMAGES}"
        )
    loaded: list[tuple[str, str, bytes]] = []
    total = 0
    for raw in paths:
        path = Path(raw)
        try:
            data = path.read_bytes()
        except OSError as exc:
            raise ImageGenerationError(f"cannot read --image {raw}: {exc}") from exc
        if not data:
            raise ImageGenerationError(f"--image {raw} is empty")
        total += len(data)
        if total > MAX_INPUT_BYTES:
            raise ImageGenerationError(
                f"reference images total more than {MAX_INPUT_BYTES // (1024 * 1024)} MiB; "
                "downscale them before the call"
            )
        mime = mimetypes.guess_type(path.name)[0] or "image/png"
        if mime not in {"image/png", "image/jpeg", "image/webp"}:
            raise ImageGenerationError(
                f"--image {raw}: {mime} is not an accepted reference format "
                "(png, jpeg or webp)"
            )
        loaded.append((path.name, mime, data))
    return loaded


def _multipart(fields: dict[str, str],
               files: list[tuple[str, str, str, bytes]]) -> tuple[bytes, str]:
    """Encode a multipart/form-data body. `files` = (field, filename, mime, data)."""
    boundary = f"----gptimage{secrets.token_hex(16)}"
    marker = f"--{boundary}".encode()
    parts: list[bytes] = []
    for name, value in fields.items():
        parts += [
            marker,
            f'Content-Disposition: form-data; name="{name}"'.encode(),
            b"",
            str(value).encode("utf-8"),
        ]
    for name, filename, mime, data in files:
        parts += [
            marker,
            (f'Content-Disposition: form-data; name="{name}"; '
             f'filename="{filename}"').encode(),
            f"Content-Type: {mime}".encode(),
            b"",
            data,
        ]
    parts += [f"--{boundary}--".encode(), b""]
    return b"\r\n".join(parts), f"multipart/form-data; boundary={boundary}"


def _request_multipart(
    endpoint: str,
    *,
    fields: dict[str, str],
    files: list[tuple[str, str, str, bytes]],
    timeout: int,
    max_attempts: int,
) -> tuple[dict[str, Any], str | None]:
    """`_request_json`'s retry behaviour, for a body the API wants as form-data."""
    body, content_type = _multipart(fields, files)
    for attempt in range(1, max_attempts + 1):
        request = urllib.request.Request(
            f"{API_ROOT}{endpoint}",
            data=body,
            headers={
                "Authorization": f"Bearer {_api_key()}",
                "User-Agent": "flutter-gambling-studio-gpt-image/1.0",
                "Content-Type": content_type,
            },
            method="POST",
        )
        try:
            with urllib.request.urlopen(request, timeout=timeout) as response:
                payload = response.read()
                request_id = response.headers.get("x-request-id")
                try:
                    decoded = json.loads(payload)
                except json.JSONDecodeError as exc:
                    raise ImageGenerationError(
                        "OpenAI Images API returned invalid JSON"
                    ) from exc
                if not isinstance(decoded, dict):
                    raise ImageGenerationError(
                        "OpenAI Images API returned an unexpected JSON value"
                    )
                return decoded, request_id
        except urllib.error.HTTPError as exc:
            error_body = exc.read()
            if exc.code in RETRYABLE_HTTP_STATUS and attempt < max_attempts:
                retry_after = exc.headers.get("Retry-After")
                try:
                    delay = min(30.0, max(1.0, float(retry_after or 2**attempt)))
                except ValueError:
                    delay = float(2**attempt)
                print(
                    f"retryable OpenAI HTTP {exc.code}; retrying in {delay:g}s "
                    f"({attempt}/{max_attempts})",
                    file=sys.stderr,
                )
                time.sleep(delay)
                continue
            raise ImageGenerationError(_error_message(exc.code, error_body)) from exc
        except urllib.error.URLError as exc:
            # As in _request_json: an ambiguous failure could bill a duplicate
            # image, so the retry decision is the caller's.
            raise ImageGenerationError(
                f"OpenAI Images API network error: {exc.reason}"
            ) from exc

    raise ImageGenerationError("OpenAI Images API request exhausted all attempts")


def _decode_image(payload: dict[str, Any]) -> bytes:
    data = payload.get("data")
    if not isinstance(data, list) or not data or not isinstance(data[0], dict):
        raise ImageGenerationError("OpenAI Images API response has no data[0]")
    encoded = data[0].get("b64_json")
    if not isinstance(encoded, str) or not encoded:
        raise ImageGenerationError(
            "OpenAI Images API response has no data[0].b64_json"
        )
    try:
        return base64.b64decode(encoded, validate=True)
    except (ValueError, TypeError) as exc:
        raise ImageGenerationError(
            "OpenAI Images API returned invalid base64 image data"
        ) from exc


def _png_dimensions(image: bytes) -> tuple[int, int]:
    if len(image) < 24 or not image.startswith(PNG_SIGNATURE):
        raise ImageGenerationError("generated file is not a valid PNG")
    if image[12:16] != b"IHDR":
        raise ImageGenerationError("generated PNG has no IHDR chunk")
    width, height = struct.unpack(">II", image[16:24])
    if width < 1 or height < 1:
        raise ImageGenerationError("generated PNG has invalid dimensions")
    return width, height


def _write_atomic(path: Path, image: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temp_path: Path | None = None
    try:
        with tempfile.NamedTemporaryFile(
            mode="wb", prefix=f".{path.name}.", suffix=".tmp", dir=path.parent, delete=False
        ) as handle:
            handle.write(image)
            handle.flush()
            os.fsync(handle.fileno())
            temp_path = Path(handle.name)
        os.replace(temp_path, path)
    finally:
        if temp_path is not None and temp_path.exists():
            temp_path.unlink()


def _probe(args: argparse.Namespace) -> int:
    payload, request_id = _request_json(
        "GET",
        f"/models/{MODEL}",
        timeout=args.timeout,
        max_attempts=args.max_attempts,
    )
    returned_model = payload.get("id")
    if returned_model != MODEL:
        raise ImageGenerationError(
            f"model probe returned {returned_model!r}, expected {MODEL!r}"
        )
    suffix = f" request_id={request_id}" if request_id else ""
    print(f"GPT Image 2 available: model={returned_model}{suffix}")
    return 0


def _generate(args: argparse.Namespace) -> int:
    prompt = _read_prompt(args)
    payload = {
        "model": MODEL,
        "prompt": prompt,
        "n": 1,
        "size": args.size,
        "quality": args.quality,
        "output_format": "png",
        "background": "opaque",
    }
    response, request_id = _request_json(
        "POST",
        "/images/generations",
        payload=payload,
        timeout=args.timeout,
        max_attempts=args.max_attempts,
    )
    image = _decode_image(response)
    width, height = _png_dimensions(image)
    output = Path(args.out)
    _write_atomic(output, image)
    suffix = f" request_id={request_id}" if request_id else ""
    print(
        f"GPT Image 2 generated: {output} "
        f"({width}x{height}, {len(image) // 1024} KiB){suffix}"
    )
    return 0


def _edit(args: argparse.Namespace) -> int:
    """One finished picture built FROM the game's own files, not described to it.

    `generate` can only be told what the hero and the symbols look like, and a
    described symbol comes back similar rather than identical — which is the
    defect that got a storefront returned. `edit` hands the model the shipped
    PNGs (and usually a composed layout draft) as reference images, so it can
    render those exact objects into the scene with real perspective, volume and
    contact instead of the flat paste-up a compositor can produce.
    """
    prompt = _read_prompt(args)
    images = _read_input_images(args.image)
    fields = {
        "model": MODEL,
        "prompt": prompt,
        "n": "1",
        "size": args.size,
        "quality": args.quality,
        "output_format": "png",
        "input_fidelity": args.fidelity,
    }
    files = [("image[]", name, mime, data) for name, mime, data in images]
    response, request_id = _request_multipart(
        "/images/edits",
        fields=fields,
        files=files,
        timeout=args.timeout,
        max_attempts=args.max_attempts,
    )
    image = _decode_image(response)
    width, height = _png_dimensions(image)
    output = Path(args.out)
    _write_atomic(output, image)
    suffix = f" request_id={request_id}" if request_id else ""
    print(
        f"GPT Image 2 edited: {output} "
        f"({width}x{height}, {len(image) // 1024} KiB) "
        f"from {len(images)} reference image{'' if len(images) == 1 else 's'} "
        f"at {args.fidelity} fidelity{suffix}"
    )
    return 0


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Generate PNG game assets through OpenAI GPT Image 2"
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    def common(subparser: argparse.ArgumentParser) -> None:
        subparser.add_argument(
            "--timeout",
            type=int,
            default=600,
            help="request timeout in seconds (default: 600)",
        )
        subparser.add_argument(
            "--max-attempts",
            type=int,
            choices=range(1, 4),
            default=2,
            metavar="{1,2,3}",
            help="attempts for explicit retryable HTTP statuses (default: 2)",
        )

    probe = subparsers.add_parser("probe", help="verify GPT Image 2 model access")
    common(probe)
    probe.set_defaults(handler=_probe)

    generate = subparsers.add_parser("generate", help="generate one PNG")
    prompt_group = generate.add_mutually_exclusive_group(required=True)
    prompt_group.add_argument("--prompt", help="image prompt")
    prompt_group.add_argument("--prompt-file", help="UTF-8 file containing the prompt")
    generate.add_argument("--out", required=True, help="destination .png path")
    generate.add_argument(
        "--size",
        type=_validate_size,
        default="1024x1024",
        help="auto or WIDTHxHEIGHT; edges must be multiples of 16",
    )
    generate.add_argument(
        "--quality",
        choices=("low", "medium", "high", "auto"),
        default="high",
    )
    common(generate)
    generate.set_defaults(handler=_generate)

    edit = subparsers.add_parser(
        "edit",
        help="render one PNG FROM reference images — the game's own assets, so the "
             "objects in the result are the objects in the app",
    )
    edit_prompt = edit.add_mutually_exclusive_group(required=True)
    edit_prompt.add_argument("--prompt", help="image prompt")
    edit_prompt.add_argument("--prompt-file", help="UTF-8 file containing the prompt")
    edit.add_argument(
        "--image",
        action="append",
        default=[],
        required=True,
        metavar="PNG",
        help="a reference image. Repeatable, and ORDER MATTERS: pass the layout "
             "draft first, then one file per object whose identity must survive "
             f"(max {MAX_INPUT_IMAGES})",
    )
    edit.add_argument("--out", required=True, help="destination .png path")
    edit.add_argument(
        "--size",
        type=_validate_size,
        default="1536x1024",
        help="auto or WIDTHxHEIGHT; edges must be multiples of 16",
    )
    edit.add_argument(
        "--quality",
        choices=("low", "medium", "high", "auto"),
        default="high",
    )
    edit.add_argument(
        "--fidelity",
        choices=("high", "low"),
        default="high",
        help="how tightly the reference images' detail is preserved. Keep it high "
             "whenever an object has to come back recognisably the same (default: high)",
    )
    common(edit)
    edit.set_defaults(handler=_edit)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    try:
        return int(args.handler(args))
    except ImageGenerationError as exc:
        print(f"GPT Image 2 error: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
