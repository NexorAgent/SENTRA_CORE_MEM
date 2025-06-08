#!/usr/bin/env python3
"""Batch compression utility using zmem_encoder."""
import json
import sys
from pathlib import Path
import base64
import zlib

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.zmem_encoder import encode_zmem


def compress_directory(input_dir: Path, output_dir: Path) -> dict:
    output_dir.mkdir(parents=True, exist_ok=True)
    report = {}
    index_path = output_dir / "memory_index.json"
    for txt in input_dir.glob("*.txt"):
        content = txt.read_text(encoding="utf-8")
        base = txt.stem
        encode_zmem(
            content=content,
            ctx_tag=base,
            zlib_txt_out=str(output_dir / f"{base}.l64.t"),
            zlib_bin_out=str(output_dir / f"{base}.l64.b"),
            zmem_src_out=str(output_dir / f"{base}.src"),
            zmem_bin_out=str(output_dir / f"{base}.zmem"),
            update_dict_path=str(index_path),
        )
        comp_data = base64.b64decode((output_dir / f"{base}.zmem").read_text())
        report[txt.name] = len(comp_data) / len(content.encode("utf-8"))
    (output_dir / "compression_report.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
    return report


def main():
    if len(sys.argv) != 3:
        print("Usage: batch_compress.py <input_dir> <output_dir>")
        return 1
    report = compress_directory(Path(sys.argv[1]), Path(sys.argv[2]))
    print(json.dumps(report, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
