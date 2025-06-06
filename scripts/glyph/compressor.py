import base64
import zlib
from pathlib import Path
from typing import Iterable
from .glyph_generator import compress_text, decompress_text

class Compressor:
    GLYPH = "glyph"
    ZLIB = "zlib"
    BOTH = "glyph_zlib"

    def __init__(self, mode: str):
        if mode not in {self.GLYPH, self.ZLIB, self.BOTH}:
            raise ValueError("invalid mode")
        self.mode = mode

    def compress(self, text: str) -> str:
        if self.mode == self.GLYPH:
            return compress_text(text)
        if self.mode == self.ZLIB:
            return base64.b85encode(zlib.compress(text.encode("utf-8"))).decode("utf-8")
        glyph = compress_text(text)
        return base64.b85encode(zlib.compress(glyph.encode("utf-8"))).decode("utf-8")

    def decompress(self, data: str) -> str:
        if self.mode == self.GLYPH:
            return decompress_text(data)
        if self.mode == self.ZLIB:
            return zlib.decompress(base64.b85decode(data)).decode("utf-8")
        glyph = zlib.decompress(base64.b85decode(data)).decode("utf-8")
        return decompress_text(glyph)
