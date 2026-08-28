from __future__ import annotations

import base64
import email
import importlib.util
import struct
import tempfile
import unittest
from pathlib import Path


SCRIPT = Path(__file__).resolve().parents[1] / "gpt_image.py"
SPEC = importlib.util.spec_from_file_location("gpt_image", SCRIPT)
assert SPEC and SPEC.loader
gpt_image = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(gpt_image)


def png_header(width: int = 1024, height: int = 1024) -> bytes:
    return (
        gpt_image.PNG_SIGNATURE
        + struct.pack(">I", 13)
        + b"IHDR"
        + struct.pack(">II", width, height)
        + b"\x08\x06\x00\x00\x00"
    )


class GptImageTests(unittest.TestCase):
    def test_validate_size_accepts_supported_square(self) -> None:
        self.assertEqual(gpt_image._validate_size("1024x1024"), "1024x1024")

    def test_validate_size_rejects_non_multiple_of_16(self) -> None:
        with self.assertRaises(Exception):
            gpt_image._validate_size("1025x1024")

    def test_decode_and_validate_png(self) -> None:
        expected = png_header(1536, 1024)
        payload = {
            "data": [{"b64_json": base64.b64encode(expected).decode("ascii")}]
        }
        image = gpt_image._decode_image(payload)
        self.assertEqual(gpt_image._png_dimensions(image), (1536, 1024))

    def test_decode_rejects_missing_image(self) -> None:
        with self.assertRaises(gpt_image.ImageGenerationError):
            gpt_image._decode_image({"data": []})

    def test_error_message_extracts_api_error(self) -> None:
        body = b'{"error":{"message":"model access denied","code":"access_denied"}}'
        message = gpt_image._error_message(403, body)
        self.assertIn("model access denied", message)
        self.assertIn("access_denied", message)


if __name__ == "__main__":
    unittest.main()


class EditReferenceTests(unittest.TestCase):
    """`edit` exists so the game's own files can BE the picture's objects.

    `generate` can only be told what a symbol looks like, and a described symbol
    comes back similar rather than identical — the defect that got a storefront
    returned. These cover the plumbing that carries the real files to the API.
    """

    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        self.dir = Path(self._tmp.name)

    def _png(self, name: str, body: bytes = b"DATA") -> str:
        path = self.dir / name
        path.write_bytes(png_header() + body)
        return str(path)

    def test_binary_references_survive_the_multipart_body(self) -> None:
        body, content_type = gpt_image._multipart(
            {"model": "gpt-image-2", "prompt": "an integrated scene é"},
            [("image[]", "draft.png", "image/png", png_header() + b"\r\n--boundary"),
             ("image[]", "hero.png", "image/png", b"\x89PNG\r\n\x1a\nHERO")])
        message = email.message_from_bytes(
            f"Content-Type: {content_type}\r\nMIME-Version: 1.0\r\n\r\n".encode() + body)
        self.assertTrue(message.is_multipart())
        parts = message.get_payload()
        self.assertEqual(parts[1].get_payload(decode=True),
                         "an integrated scene é".encode("utf-8"))
        # Bytes that happen to look like a boundary must not split the body.
        self.assertEqual(parts[2].get_payload(decode=True),
                         png_header() + b"\r\n--boundary")
        self.assertEqual(parts[3].get_payload(decode=True), b"\x89PNG\r\n\x1a\nHERO")

    def test_references_keep_the_order_they_were_passed_in(self) -> None:
        # The draft is first because it is the layout; the objects follow in the
        # order the prompt names them.
        loaded = gpt_image._read_input_images(
            [self._png("draft.png"), self._png("hero.png"), self._png("board.png")])
        self.assertEqual([name for name, _, _ in loaded],
                         ["draft.png", "hero.png", "board.png"])

    def test_an_unusable_reference_is_refused_before_the_call(self) -> None:
        with self.assertRaises(gpt_image.ImageGenerationError):
            gpt_image._read_input_images([])
        with self.assertRaises(gpt_image.ImageGenerationError):
            gpt_image._read_input_images([str(self.dir / "missing.png")])
        (self.dir / "notes.txt").write_text("not an image")
        with self.assertRaises(gpt_image.ImageGenerationError):
            gpt_image._read_input_images([str(self.dir / "notes.txt")])
        with self.assertRaises(gpt_image.ImageGenerationError):
            gpt_image._read_input_images(
                [self._png("a.png")] * (gpt_image.MAX_INPUT_IMAGES + 1))

    def test_edit_defaults_to_high_input_fidelity(self) -> None:
        # The whole point of the pass: drop fidelity and the objects drift.
        args = gpt_image._parser().parse_args(
            ["edit", "--prompt", "x", "--image", "a.png", "--out", "b.png"])
        self.assertEqual(args.fidelity, "high")
