import base64
import json
import zlib
import re
from typing import Dict

from .glyph_generator import (
    compress_text,
    decompress_text,
    decompress_with_dict,
    export_dict,
    compress_with_dict,
)


def make_mem_block(
    fields: Dict[str, str],
    text: str,
    *,
    include_mapping: bool = False,
    mapping: Dict[str, str] | None = None,
) -> str:
    """Return a MEM.BLOCK string from fields and input text.

    If ``mapping`` is provided, it is used for compression and optionally
    embedded when ``include_mapping`` is True. Otherwise the persistent
    dictionary is used.
    """
    if mapping is not None:
        compressed_glyph = compress_with_dict(text, mapping)
    else:
        compressed_glyph = compress_text(text)
    z = base64.b85encode(zlib.compress(compressed_glyph.encode("utf-8"))).decode("utf-8")
    parts = [
        "⦿MEM.BLOCK🧠∴",
        f"⟁ID⟶{fields.get('ID','')}↯",
        f"⟁TS⟶{fields.get('TS','')}↯",
        f"⟁INT⟶{fields.get('INT','')}↯",
        f"⟁Σ⟶{fields.get('Σ','')}↯",
        f"⟁CMPZ⟶ƛ:{z}↯",
        "⟁SEAL⟶✅SENTRA",
    ]
    block = "".join(parts)
    if include_mapping:
        mapping_json = json.dumps(mapping if mapping is not None else export_dict(), ensure_ascii=False)
        block += "\n" + mapping_json
    return block


def decode_mem_block(block: str) -> str:
    """Decode a MEM.BLOCK string and return original text."""
    if "\n" in block:
        block_line, mapping_part = block.split("\n", 1)
        try:
            mapping = json.loads(mapping_part)
        except json.JSONDecodeError:
            mapping = None
    else:
        block_line = block
        mapping = None

    m = re.search(r"⟁CMPZ⟶ƛ:([^↯]+)", block_line)
    if not m:
        return block
    z = base64.b85decode(m.group(1))
    compressed_glyph = zlib.decompress(z).decode("utf-8")
    if mapping:
        return decompress_with_dict(compressed_glyph, mapping)
    return decompress_text(compressed_glyph)


if __name__ == "__main__":
    import argparse
    from pathlib import Path
    from datetime import datetime

    parser = argparse.ArgumentParser(description="Create a MEM.BLOCK from a text file")
    parser.add_argument("input", help="source text file")
    parser.add_argument("-o", "--output", help="destination block file")
    parser.add_argument("--include-mapping", action="store_true", help="embed mapping in the block")
    parser.add_argument("--mapping-file", help="path to save the glyph mapping")
    parser.add_argument("--obfuscate", action="store_true", help="randomize glyph assignments")
    args = parser.parse_args()

    text = Path(args.input).read_text(encoding="utf-8")
    fields = {
        "ID": "ZCLI",
        "TS": datetime.now().strftime("%Y-%m-%dT%H:%M"),
        "INT": "CLI.COMPRESS",
        "Σ": "MEM.GLYPH",
    }

    mapping = None
    if args.obfuscate:
        from .glyph_generator import randomize_mapping, export_dict

        mapping = randomize_mapping(export_dict())

    block = make_mem_block(fields, text, include_mapping=args.include_mapping, mapping=mapping)

    if args.output:
        Path(args.output).write_text(block, encoding="utf-8")
    else:
        print(block)

    if mapping is not None:
        map_path = args.mapping_file
        if not map_path:
            base = args.output or args.input
            map_path = str(Path(base).with_suffix(".map.json"))
        Path(map_path).write_text(json.dumps(mapping, ensure_ascii=False, indent=2), encoding="utf-8")
