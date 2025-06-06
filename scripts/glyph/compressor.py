"""Generic text compressor using various mapping dictionaries."""

from __future__ import annotations

import argparse
import json
import pathlib
import re
from typing import Dict

from .glyph_generator import dict_file


class Compressor:
    """Compress and decompress text using mapping dictionaries."""

    MODES = {
        "visual": "glyph_dict.json",
        "abbrev": "abbreviations_dict.json",
        "alphanumeric": "alphanumeric_dict.json",
        "custom": "custom_dict.json",
    }

    def __init__(self, mode: str = "visual") -> None:
        if mode not in self.MODES:
            raise ValueError(f"Unknown mode: {mode}")
        self.mode = mode
        self.dict_path = self._resolve_path()
        self.mapping: Dict[str, str] = self._load_mapping()

    def _resolve_path(self) -> pathlib.Path:
        base = dict_file().parent
        return base / self.MODES[self.mode]

    def _load_mapping(self) -> Dict[str, str]:
        if self.dict_path.exists():
            return json.loads(self.dict_path.read_text(encoding="utf-8"))
        return {}

    def compress(self, text: str) -> str:
        mapping = self.mapping
        for term, token in sorted(mapping.items(), key=lambda x: len(x[0]), reverse=True):
            pattern = rf"\b{re.escape(term)}\b"
            text = re.sub(pattern, lambda _m, t=token: t, text)
        return text

    def decompress(self, text: str) -> str:
        mapping = self.mapping
        for term, token in sorted(mapping.items(), key=lambda x: len(x[1]), reverse=True):
            text = text.replace(token, term)
        return text


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description="Compress a text file using a mapping dictionary")
    parser.add_argument("--mode", choices=list(Compressor.MODES.keys()), default="visual")
    parser.add_argument("input")
    parser.add_argument("output")
    args = parser.parse_args(argv)

    comp = Compressor(args.mode)
    data = pathlib.Path(args.input).read_text(encoding="utf-8")
    compressed = comp.compress(data)
    pathlib.Path(args.output).write_text(compressed, encoding="utf-8")


if __name__ == "__main__":
    main()
