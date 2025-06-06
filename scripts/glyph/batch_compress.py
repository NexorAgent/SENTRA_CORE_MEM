import argparse
import base64
import csv
import pathlib
import zlib
from typing import Iterable, Tuple

from .glyph_generator import compress_text


def _compress_content(text: str, mode: str) -> str:
    """Compress text using the selected mode."""
    if mode == "glyph":
        return compress_text(text)
    if mode == "zlib":
        compressed = zlib.compress(text.encode("utf-8"))
        return base64.b85encode(compressed).decode("ascii")
    raise ValueError(f"Unknown mode: {mode}")


def _process_file(src: pathlib.Path, dst: pathlib.Path, mode: str) -> Tuple[int, int]:
    """Compress one file and return (original_size, compressed_size)."""
    try:
        content = src.read_text(encoding="utf-8")
    except Exception:
        content = src.read_text(errors="ignore")
    compressed = _compress_content(content, mode)
    dst.parent.mkdir(parents=True, exist_ok=True)
    dst.write_text(compressed, encoding="utf-8")
    return len(content.encode("utf-8")), len(compressed.encode("utf-8"))


def _iter_text_files(root: pathlib.Path) -> Iterable[pathlib.Path]:
    """Yield all .txt files under root."""
    for path in root.rglob("*.txt"):
        if path.is_file():
            yield path


def write_report(entries: Iterable[Tuple[str, int, int]], report_path: pathlib.Path) -> None:
    """Write CSV or Markdown report depending on extension."""
    if report_path.suffix.lower() == ".md":
        lines = ["| File | Original | Compressed | Ratio |", "| --- | ---:| ---:| ---:|"]
        for rel, orig, comp in entries:
            ratio = comp / orig if orig else 0
            lines.append(f"| {rel} | {orig} | {comp} | {ratio:.2f} |")
        report_path.write_text("\n".join(lines), encoding="utf-8")
    else:
        with report_path.open("w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(["file", "original", "compressed", "ratio"])
            for rel, orig, comp in entries:
                ratio = comp / orig if orig else 0
                writer.writerow([rel, orig, comp, f"{ratio:.2f}"])


def main() -> None:
    parser = argparse.ArgumentParser(description="Batch compress text files")
    parser.add_argument("src", help="Source directory")
    parser.add_argument("dst", help="Destination directory")
    parser.add_argument("--mode", choices=["glyph", "zlib"], default="glyph", help="Compression mode")
    parser.add_argument("--report", help="Path to CSV or Markdown report")
    args = parser.parse_args()

    src = pathlib.Path(args.src)
    dst = pathlib.Path(args.dst)
    report = pathlib.Path(args.report) if args.report else dst / "report.csv"
    entries = []
    for path in _iter_text_files(src):
        rel = path.relative_to(src)
        dest_file = dst / rel
        orig, comp = _process_file(path, dest_file, args.mode)
        entries.append((str(rel), orig, comp))
    write_report(entries, report)


if __name__ == "__main__":
    main()
