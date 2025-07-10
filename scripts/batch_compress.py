#!/usr/bin/env python3
"""Batch compress text files using glyph encoding or zlib.

Usage:
    python batch_compress.py SRC_DIR DEST_DIR [--mode glyph|zlib] [--report path/to/report.csv|.md] [--obfuscate]

- SRC_DIR : dossier source contenant les fichiers .txt
- DEST_DIR : dossier destination pour les fichiers compressés
- --mode : glyph (par défaut), zlib, pour choisir l’algorithme de compression
- --report : chemin du rapport de compression (CSV ou Markdown, auto selon extension)
- --obfuscate : encode chaque fichier en MEM.BLOCK SANS mapping (plus sûr pour le partage)

Exemple :
    python batch_compress.py ./in ./out --mode glyph --report ./out/report.md --obfuscate
"""

import argparse
import base64
import csv
import zlib
from datetime import datetime
from pathlib import Path
from typing import Iterable, Tuple

from scripts.glyph.glyph_generator import compress_text

from .mem_block import make_mem_block


def compress_content(text: str, mode: str, obfuscate: bool, src_name: str = "") -> str:
    """Compress text using glyph or zlib, option obfuscate (MEM.BLOCK sans mapping)."""
    if obfuscate:
        block = make_mem_block(
            {
                "ID": "BATCH",
                "TS": datetime.now().isoformat(timespec="seconds"),
                "INT": src_name or "BATCH",
                "Σ": "MEM.GLYPH",
            },
            text,
            include_mapping=False,
        )
        return block
    if mode == "glyph":
        return compress_text(text)
    if mode == "zlib":
        compressed = zlib.compress(text.encode("utf-8"))
        return base64.b85encode(compressed).decode("ascii")
    raise ValueError(f"Unknown mode: {mode}")


def process_file(src: Path, dst: Path, mode: str, obfuscate: bool) -> Tuple[int, int]:
    """Compress one file and return (original_size, compressed_size)."""
    try:
        content = src.read_text(encoding="utf-8")
    except Exception:
        content = src.read_text(errors="ignore")
    compressed = compress_content(content, mode, obfuscate, src.stem)
    dst.parent.mkdir(parents=True, exist_ok=True)
    dst.write_text(compressed, encoding="utf-8")
    return len(content.encode("utf-8")), len(compressed.encode("utf-8"))


def iter_text_files(root: Path) -> Iterable[Path]:
    """Yield all .txt files under root recursively."""
    for path in root.rglob("*.txt"):
        if path.is_file():
            yield path


def write_report(entries: Iterable[Tuple[str, int, int]], report_path: Path) -> None:
    """Write CSV or Markdown report depending on extension."""
    if report_path.suffix.lower() == ".md":
        lines = [
            "| File | Original | Compressed | Ratio |",
            "| --- | ---:| ---:| ---:|",
        ]
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


def main():
    parser = argparse.ArgumentParser(
        description="Batch compress text files using glyph or zlib"
    )
    parser.add_argument("src", type=Path, help="Source directory (recursif, *.txt)")
    parser.add_argument("dst", type=Path, help="Destination directory")
    parser.add_argument(
        "--mode",
        choices=["glyph", "zlib"],
        default="glyph",
        help="Compression mode (default: glyph)",
    )
    parser.add_argument(
        "--report", type=Path, help="Path to CSV or Markdown report (auto .csv/.md)"
    )
    parser.add_argument(
        "--obfuscate",
        action="store_true",
        help="Use MEM.BLOCK compression without mapping (glyph only)",
    )
    args = parser.parse_args()

    src = args.src
    dst = args.dst
    report_path = (
        args.report
        if args.report
        else dst
        / ("report.md" if args.mode == "glyph" and args.obfuscate else "report.csv")
    )

    entries = []
    for path in iter_text_files(src):
        rel = path.relative_to(src)
        dest_file = dst / rel
        orig, comp = process_file(path, dest_file, args.mode, args.obfuscate)
        entries.append((str(rel), orig, comp))
    write_report(entries, report_path)


if __name__ == "__main__":
    main()
