import base64
import csv
import zlib
from pathlib import Path

from .glyph_generator import compress_text

ROOT = Path(__file__).resolve().parents[2]
RAW_DIR = ROOT / "logs_raw"
OUT_DIR = ROOT / "logs_compressed"


def compress_file(path: Path) -> tuple[str, int, int, float]:
    """Compress a file and return stats."""
    text = path.read_text(encoding="utf-8", errors="ignore")
    original_size = len(text.encode("utf-8"))
    glyph = compress_text(text)
    encoded = base64.b85encode(zlib.compress(glyph.encode("utf-8"), level=9))
    rel = path.relative_to(RAW_DIR)
    out_path = OUT_DIR / rel
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_bytes(encoded)
    compressed_size = len(encoded)
    ratio = compressed_size / original_size if original_size else 0
    return rel.as_posix(), original_size, compressed_size, ratio


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    files = [p for p in RAW_DIR.rglob("*") if p.is_file()]
    stats = [compress_file(p) for p in files]
    summary = OUT_DIR / "compression_summary.csv"
    with summary.open("w", encoding="utf-8", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["file", "original_bytes", "compressed_bytes", "ratio"])
        for row in stats:
            writer.writerow([row[0], row[1], row[2], f"{row[3]:.2f}"])


if __name__ == "__main__":
    main()
