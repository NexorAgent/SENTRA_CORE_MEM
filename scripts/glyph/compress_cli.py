#!/usr/bin/env python3
"""CLI to compress a text file into a MEM.BLOCK."""
import argparse
import json
from pathlib import Path

from .mem_block import make_mem_block


def main() -> None:
    p = argparse.ArgumentParser(description="Compress a text file into a MEM.BLOCK")
    p.add_argument("input", help="Input text file")
    p.add_argument("-o", "--output", required=True, help="Destination MEM.BLOCK file")
    p.add_argument("--id", default="ZCLI", help="ID field for the block")
    p.add_argument("--obfuscate", action="store_true", help="Randomize glyph assignments")
    p.add_argument("--mapping-out", help="Path to write the glyph mapping")
    args = p.parse_args()

    text = Path(args.input).read_text(encoding="utf-8")
    fields = {"ID": args.id, "TS": "", "INT": "CLI", "Σ": "MEM.GLYPH"}

    if args.obfuscate:
        block, mapping = make_mem_block(fields, text, obfuscate=True)
        Path(args.output).write_text(block, encoding="utf-8")
        if args.mapping_out:
            Path(args.mapping_out).write_text(
                json.dumps(mapping, ensure_ascii=False, indent=2), encoding="utf-8"
            )
    else:
        include = args.mapping_out is not None
        block = make_mem_block(fields, text, include_mapping=include)
        Path(args.output).write_text(block, encoding="utf-8")
        if args.mapping_out and include:
            mapping = json.loads(block.split("\n", 1)[1])
            Path(args.mapping_out).write_text(
                json.dumps(mapping, ensure_ascii=False, indent=2), encoding="utf-8"
            )

    print(f"Wrote MEM.BLOCK to {args.output}")
    if args.mapping_out:
        print(f"Mapping saved to {args.mapping_out}")


if __name__ == "__main__":
    main()
