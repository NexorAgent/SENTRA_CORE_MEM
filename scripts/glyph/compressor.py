import json
import re
from pathlib import Path
from typing import Dict

from .glyph_generator import (
    dict_file,
    compress_text as visual_compress,
    decompress_text as visual_decompress,
)


class Compressor:
    """Generic text compressor with multiple modes."""

    MODES = {"visual", "abbrev", "alphanumeric", "custom"}

    def __init__(self, mode: str = "visual") -> None:
        if mode not in self.MODES:
            raise ValueError(f"Invalid mode: {mode}")
        self.mode = mode
        self.mapping: Dict[str, str] = self.load_mapping()

    # ------------------------------------------------------------------
    # Mapping helpers
    # ------------------------------------------------------------------
    def mapping_file(self, path: str | Path | None = None) -> Path:
        return Path(path) if path else dict_file()

    def load_mapping(self, path: str | Path | None = None) -> Dict[str, str]:
        f = self.mapping_file(path)
        if f.exists():
            try:
                return json.loads(f.read_text(encoding="utf-8"))
            except Exception:
                return {}
        return {}

    def save_mapping(self, path: str | Path | None = None) -> None:
        f = self.mapping_file(path)
        f.write_text(json.dumps(self.mapping, indent=2, ensure_ascii=False), encoding="utf-8")

    # ------------------------------------------------------------------
    # Token generation strategies
    # ------------------------------------------------------------------
    def _token_abbrev(self, term: str) -> str:
        base = term[:3]
        token = base
        counter = 1
        existing = set(self.mapping.values())
        while token in existing:
            token = f"{base}{counter}"
            counter += 1
        return token

    def _token_alphanumeric(self) -> str:
        existing = set(self.mapping.values())
        idx = 0
        while True:
            token = f"§{idx:X}"
            if token not in existing:
                return token
            idx += 1

    # ------------------------------------------------------------------
    # Compression / decompression
    # ------------------------------------------------------------------
    def compress(self, text: str) -> str:
        if self.mode == "visual":
            return visual_compress(text)

        words = re.findall(r"\b\w+\b", text)
        for w in set(words):
            if w not in self.mapping:
                if self.mode == "abbrev":
                    self.mapping[w] = self._token_abbrev(w)
                elif self.mode == "alphanumeric":
                    self.mapping[w] = self._token_alphanumeric()
                elif self.mode == "custom":
                    # do not create new tokens in custom mode
                    continue
        if self.mode != "custom":
            self.save_mapping()
        for term, token in sorted(self.mapping.items(), key=lambda x: len(x[0]), reverse=True):
            text = re.sub(rf"\b{re.escape(term)}\b", token, text)
        return text

    def decompress(self, text: str) -> str:
        if self.mode == "visual":
            return visual_decompress(text)
        for term, token in sorted(self.mapping.items(), key=lambda x: len(x[1]), reverse=True):
            text = text.replace(token, term)
        return text


# ----------------------------------------------------------------------
# CLI
# ----------------------------------------------------------------------
if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Compress text using glyph compressor")
    parser.add_argument("--mode", choices=sorted(Compressor.MODES), default="visual")
    parser.add_argument("input")
    parser.add_argument("output")
    args = parser.parse_args()

    comp = Compressor(args.mode)
    data = Path(args.input).read_text(encoding="utf-8")
    result = comp.compress(data)
    Path(args.output).write_text(result, encoding="utf-8")
