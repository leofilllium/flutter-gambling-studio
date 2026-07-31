from __future__ import annotations

import base64
import importlib.util
import struct
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
