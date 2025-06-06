import argparse
import json
import pathlib
import re
from typing import Dict

from .glyph_generator import (
    compress_text as glyph_compress,
    decompress_text as glyph_decompress,
    dict_file,
)


class Compressor:
    """Generic text compressor supporting multiple modes."""

    def __init__(self, mode: str = "visual"):
        self.mode = mode
        self.dict_path = self._map_path()
        self.mapping = self._load_mapping()

    # -------------------------------------------------------------
    def _map_path(self) -> pathlib.Path:
        base = dict_file()
        if self.mode == "visual":
            return base
        return base.with_name(f"{self.mode}_dict.json")

    def _load_mapping(self) -> Dict[str, str]:
        if self.dict_path.exists():
            try:
                return json.loads(self.dict_path.read_text(encoding="utf-8"))
            except json.JSONDecodeError:
                return {}
        return {}

    def _save_mapping(self) -> None:
        self.dict_path.parent.mkdir(parents=True, exist_ok=True)
        self.dict_path.write_text(
            json.dumps(self.mapping, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )

    # -------------------------------------------------------------
    def _generate_token(self, word: str) -> str:
        existing = set(self.mapping.values())
        if self.mode == "abbrev":
            base = word[:3].lower()
            token = base
            idx = 1
            while token in existing:
                token = f"{base}{idx}"
                idx += 1
            return token
        if self.mode == "alphanumeric":
            return f"T{len(self.mapping) + 1}"
        # custom mode falls back to generic numbering
        return f"C{len(self.mapping) + 1}"

    # -------------------------------------------------------------
    def compress(self, text: str) -> str:
        if self.mode == "visual":
            return glyph_compress(text)
        words = re.findall(r"\b\w+\b", text)
        for w in set(words):
            token = self.mapping.get(w)
            if not token:
                token = self._generate_token(w)
                self.mapping[w] = token
        for term, token in sorted(self.mapping.items(), key=lambda x: -len(x[0])):
            text = re.sub(rf"\b{re.escape(term)}\b", token, text)
        self._save_mapping()
        return text

    def decompress(self, text: str) -> str:
        if self.mode == "visual":
            return glyph_decompress(text)
        for term, token in sorted(self.mapping.items(), key=lambda x: len(x[1]), reverse=True):
            text = text.replace(token, term)
        return text


# -------------------------------------------------------------

def main() -> None:
    parser = argparse.ArgumentParser(
        description="Compress text files using simple glyph mappings"
    )
    parser.add_argument(
        "--mode",
        default="visual",
        choices=["visual", "abbrev", "alphanumeric", "custom"],
        help="Compression mode",
    )
    parser.add_argument("input", help="Input text file")
    parser.add_argument("output", help="Output text file")
    args = parser.parse_args()

    content = pathlib.Path(args.input).read_text(encoding="utf-8")
    comp = Compressor(args.mode)
    compressed = comp.compress(content)
    pathlib.Path(args.output).write_text(compressed, encoding="utf-8")


if __name__ == "__main__":
    main()
