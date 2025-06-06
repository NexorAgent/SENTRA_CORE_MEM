import base64
import json
import zlib
import re
from typing import Dict

from .glyph_generator import compress_text, decompress_text, decompress_with_dict, export_dict


def make_mem_block(fields: Dict[str, str], text: str, *, include_mapping: bool = False) -> str:
    """Return a MEM.BLOCK string from fields and input text."""
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
        mapping_json = json.dumps(export_dict(), ensure_ascii=False)
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
