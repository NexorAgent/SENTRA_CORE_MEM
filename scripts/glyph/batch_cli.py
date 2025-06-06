import argparse
import json
from pathlib import Path
from .compressor import Compressor


def main():
    parser = argparse.ArgumentParser(description="Batch compress files")
    parser.add_argument("mode", choices=[Compressor.GLYPH, Compressor.ZLIB, Compressor.BOTH])
    parser.add_argument("directory")
    args = parser.parse_args()

    comp = Compressor(args.mode)
    directory = Path(args.directory)
    report = {}
    for file in directory.rglob("*.txt"):
        text = file.read_text(encoding="utf-8")
        compressed = comp.compress(text)
        cpath = file.with_suffix(file.suffix + f".{args.mode}.cmp")
        cpath.write_text(compressed, encoding="utf-8")
        decompressed = comp.decompress(compressed)
        dpath = file.with_suffix(file.suffix + f".{args.mode}.dec")
        dpath.write_text(decompressed, encoding="utf-8")
        report[str(file)] = {"compressed": str(cpath), "decompressed": str(dpath)}
    report_path = directory / "compression_report.json"
    report_path.write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")


if __name__ == "__main__":
    main()
