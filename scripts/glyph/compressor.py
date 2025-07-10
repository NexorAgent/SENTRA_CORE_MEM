import argparse
import json
import os
import pathlib
import random
import re
import string
from typing import Dict, Iterable

ROOT = pathlib.Path(__file__).resolve().parents[2]
DEFAULT_DICT_DIR = ROOT / "memory"

GLYPH_POOL = list("↯⊚⟴⚡∑¤†⌇⟁⊕⚙⚖🜁🧩🌀⧉♒︎⩾⊗" + string.punctuation)
EMOJI_POOL = list("😀😁😂🤣😃😄😅😆😉😊😋😎🥳🤖👾👻")


class Compressor:
    """Generic text compressor with multiple modes."""

    _ALIAS = {
        "visual": "glyph",
        "abbrev": "abbr",
        "alphanumeric": "alphanum",
    }

    def __init__(self, mode: str = "glyph", dict_dir: pathlib.Path | None = None):
        self.mode = self._ALIAS.get(mode, mode)
        self.dict_dir = pathlib.Path(dict_dir) if dict_dir else DEFAULT_DICT_DIR
        self.mapping = self._load_dict()

    # ------------------------------------------------------------------
    # Dictionary helpers
    def dict_file(self) -> pathlib.Path:
        """Return path to dictionary file for current mode."""
        filename = f"{self.mode}_dict.json"
        env = os.environ.get(f"{self.mode.upper()}_DICT_PATH")
        return pathlib.Path(env) if env else self.dict_dir / filename

    def _load_dict(self) -> Dict[str, str]:
        path = self.dict_file()
        if path.exists():
            return json.loads(path.read_text(encoding="utf-8"))
        return {}

    def _save_dict(self) -> None:
        path = self.dict_file()
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(
            json.dumps(self.mapping, indent=2, ensure_ascii=False),
            encoding="utf-8",
        )

    # backward compatibility
    def _save_mapping(self) -> None:
        self._save_dict()

    # ------------------------------------------------------------------
    # Token generation
    def _generate_token(self, used: Iterable[str]) -> str:
        used = set(used)
        if self.mode == "emoji":
            pool = EMOJI_POOL
            token = random.choice(pool)
            while token in used:
                token = random.choice(pool)
            return token
        elif self.mode == "abbr":
            token = "".join(random.choice(string.ascii_uppercase) for _ in range(3))
            while token in used:
                token = "".join(random.choice(string.ascii_uppercase) for _ in range(3))
            return token
        elif self.mode == "alphanum":
            chars = string.ascii_uppercase + string.digits
            token = "".join(random.choice(chars) for _ in range(2))
            while token in used:
                token = "".join(random.choice(chars) for _ in range(2))
            return token
        # default glyph mode
        token = random.choice(GLYPH_POOL) + random.choice("0123456789abcdef")
        while token in used:
            token = random.choice(GLYPH_POOL) + random.choice("0123456789abcdef")
        return token

    # ------------------------------------------------------------------
    # Public API
    def get_token(self, term: str) -> str:
        if term not in self.mapping:
            self.mapping[term] = self._generate_token(self.mapping.values())
            self._save_dict()
        return self.mapping[term]

    def get_term(self, token: str) -> str:
        reverse = {v: k for k, v in self.mapping.items()}
        return reverse.get(token, token)

    def compress_text(self, text: str) -> str:
        words = re.findall(r"\b\w+\b", text)
        for w in set(words):
            token = self.get_token(w)
            pattern = rf"\b{re.escape(w)}\b"
            text = re.sub(pattern, lambda _m, t=token: t, text)
        return text

    def decompress_text(self, text: str) -> str:
        for term, token in sorted(
            self.mapping.items(), key=lambda x: len(x[1]), reverse=True
        ):
            text = text.replace(token, term)
        return text

    # Compatibility aliases
    def compress(self, text: str) -> str:
        return self.compress_text(text)

    def decompress(self, text: str) -> str:
        return self.decompress_text(text)


# ----------------------------------------------------------------------
# CLI entry point


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description="Compress/decompress text")
    parser.add_argument("input", help="Input text file")
    parser.add_argument("output", help="Output text file")
    parser.add_argument("--mode", default="glyph", help="Compression mode")
    parser.add_argument(
        "--decompress", action="store_true", help="Decompress instead of compress"
    )
    args = parser.parse_args(argv)

    comp = Compressor(args.mode)
    data = pathlib.Path(args.input).read_text(encoding="utf-8")
    if args.decompress:
        result = comp.decompress_text(data)
    else:
        result = comp.compress_text(data)
    pathlib.Path(args.output).write_text(result, encoding="utf-8")


if __name__ == "__main__":
    main()
