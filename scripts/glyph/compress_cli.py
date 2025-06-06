#!/usr/bin/env python3
"""Simple CLI to compress files with the glyph compressor."""
import argparse
import json
from pathlib import Path

from .glyph_generator import compress_text


def main() -> None:
    parser = argparse.ArgumentParser(description="Compress a text file using glyphs")
    parser.add_argument("input", help="Input text file")
    parser.add_argument("output", nargs="?", help="Output file for compressed text")
    parser.add_argument("--obfuscate", action="store_true", help="Randomize glyphs and save mapping")
    parser.add_argument("--map-out", default="obfuscated_map.json", help="Mapping file when using --obfuscate")
    args = parser.parse_args()

    text = Path(args.input).read_text(encoding="utf-8")
    compressed = compress_text(text, obfuscate=args.obfuscate, mapping_file=args.map_out)

    out_path = Path(args.output) if args.output else Path(args.input).with_suffix(".glyph")
    out_path.write_text(compressed, encoding="utf-8")
    if args.obfuscate:
        print(f"Mapping written to {args.map_out}")
    print(f"Compressed text written to {out_path}")


if __name__ == "__main__":
    main()
