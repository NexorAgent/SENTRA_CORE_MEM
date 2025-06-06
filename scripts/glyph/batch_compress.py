#!/usr/bin/env python3
"""Batch compress text files using glyph encoding.

Usage: python batch_compress.py SRC_DIR DEST_DIR [--mode csv|markdown] [--obfuscate]

The script recursively walks SRC_DIR, compresses each file using the glyph
library and writes the result to the mirrored path inside DEST_DIR.
A report containing the compression ratio for each file is created in
DEST_DIR as ``compression_report.csv`` or ``compression_report.md`` depending
on ``--mode``.

``--obfuscate`` compresses files into MEM.BLOCK strings without including the
mapping table for easier sharing without exposing the dictionary.
"""

from __future__ import annotations

import argparse
from pathlib import Path
from datetime import datetime
import csv

from .glyph_generator import compress_text
from .mem_block import make_mem_block


def compress_file(src: Path, dest: Path, *, obfuscate: bool) -> tuple[int, int, float]:
    """Compress ``src`` and write result to ``dest``.

    Returns original size, compressed size and ratio.
    """
    text = src.read_text(encoding="utf-8", errors="ignore")
    if obfuscate:
        block = make_mem_block(
            {
                "ID": "BATCH",
                "TS": datetime.now().isoformat(timespec="seconds"),
                "INT": src.stem,
                "Σ": "MEM.GLYPH",
            },
            text,
            include_mapping=False,
        )
        compressed = block
    else:
        compressed = compress_text(text)

    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_text(compressed, encoding="utf-8")

    original_size = len(text.encode("utf-8"))
    compressed_size = len(compressed.encode("utf-8"))
    ratio = compressed_size / original_size if original_size else 1.0
    return original_size, compressed_size, ratio


def walk_and_compress(src_dir: Path, dest_dir: Path, obfuscate: bool) -> list[tuple[str, int, int, float]]:
    """Process ``src_dir`` recursively and return report rows."""
    rows: list[tuple[str, int, int, float]] = []
    for path in src_dir.rglob("*"):
        if path.is_file():
            rel = path.relative_to(src_dir)
            dest = dest_dir / rel
            orig, comp, ratio = compress_file(path, dest, obfuscate=obfuscate)
            rows.append((str(rel), orig, comp, ratio))
    return rows


def save_report(rows: list[tuple[str, int, int, float]], dest: Path, mode: str) -> None:
    """Write CSV or Markdown report to ``dest``."""
    if mode == "markdown":
        report_path = dest / "compression_report.md"
        with report_path.open("w", encoding="utf-8") as f:
            f.write("| file | original_bytes | compressed_bytes | ratio |\n")
            f.write("|---|---|---|---|\n")
            for rel, orig, comp, ratio in rows:
                f.write(f"| {rel} | {orig} | {comp} | {ratio:.2f} |\n")
    else:
        report_path = dest / "compression_report.csv"
        with report_path.open("w", encoding="utf-8", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(["file", "original_bytes", "compressed_bytes", "ratio"])
            for rel, orig, comp, ratio in rows:
                writer.writerow([rel, orig, comp, f"{ratio:.2f}"])


def main() -> None:
    parser = argparse.ArgumentParser(description="Batch compress glyph files")
    parser.add_argument("src", type=Path, help="Source directory")
    parser.add_argument("dest", type=Path, help="Destination directory")
    parser.add_argument(
        "--mode",
        choices=["csv", "markdown"],
        default="csv",
        help="Report format",
    )
    parser.add_argument(
        "--obfuscate",
        action="store_true",
        help="Use MEM.BLOCK compression without mapping",
    )
    args = parser.parse_args()

    rows = walk_and_compress(args.src, args.dest, args.obfuscate)
    save_report(rows, args.dest, args.mode)


if __name__ == "__main__":
    main()
