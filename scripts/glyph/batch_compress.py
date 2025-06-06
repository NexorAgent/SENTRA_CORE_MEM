import argparse
import csv
import pathlib
from typing import List, Tuple

from .mem_block import make_mem_block


def _process_file(src: pathlib.Path, dst: pathlib.Path, obfuscate: bool) -> Tuple[int, int]:
    """Compress a single file and return original and compressed sizes."""
    try:
        text = src.read_text(encoding="utf-8")
    except Exception:
        return 0, 0
    compressed = make_mem_block({"ID": src.stem}, text, include_mapping=not obfuscate)
    dst.parent.mkdir(parents=True, exist_ok=True)
    dst.write_text(compressed, encoding="utf-8")
    return len(text.encode("utf-8")), len(compressed.encode("utf-8"))


def compress_directory(src_dir: pathlib.Path, dst_dir: pathlib.Path, *, mode: str = "csv", obfuscate: bool = False) -> pathlib.Path:
    """Recursively compress files from src_dir into dst_dir."""
    results: List[Tuple[str, int, int, float]] = []
    for src in src_dir.rglob("*"):
        if src.is_file():
            rel = src.relative_to(src_dir)
            dst = dst_dir / rel
            dst = dst.with_suffix(dst.suffix + ".mb")
            orig, comp = _process_file(src, dst, obfuscate)
            ratio = (comp / orig) if orig else 0
            results.append((str(rel), orig, comp, ratio))

    report_path = dst_dir / ("compression_report.csv" if mode == "csv" else "compression_report.md")
    report_path.parent.mkdir(parents=True, exist_ok=True)
    if mode == "csv":
        with report_path.open("w", encoding="utf-8", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(["file", "original", "compressed", "ratio"])
            for row in results:
                writer.writerow(row)
    else:
        with report_path.open("w", encoding="utf-8") as f:
            f.write("| File | Original | Compressed | Ratio |\n")
            f.write("| --- | --- | --- | --- |\n")
            for name, orig, comp, ratio in results:
                f.write(f"| {name} | {orig} | {comp} | {ratio:.2f} |\n")
    return report_path


def main() -> None:
    parser = argparse.ArgumentParser(description="Batch glyph compression")
    parser.add_argument("source", help="Source directory")
    parser.add_argument("dest", help="Destination directory")
    parser.add_argument("--mode", choices=["csv", "md"], default="csv", help="Report format")
    parser.add_argument("--obfuscate", action="store_true", help="Exclude glyph mapping table")
    args = parser.parse_args()

    src_dir = pathlib.Path(args.source)
    dst_dir = pathlib.Path(args.dest)
    compress_directory(src_dir, dst_dir, mode=args.mode, obfuscate=args.obfuscate)


if __name__ == "__main__":
    main()
