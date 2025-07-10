#!/usr/bin/env python3
"""Extract a simple ``mot -> glyphe`` mapping from an enriched glyph dictionary."""
import json
import argparse
import sys
from pathlib import Path


def extract(input_file: str, output_file: str) -> None:
    try:
        enriched = json.loads(Path(input_file).read_text(encoding="utf-8"))
    except FileNotFoundError:
        print(f"Error: Input file '{input_file}' not found.", file=sys.stderr)
        sys.exit(1)
    except json.JSONDecodeError as e:
        print(f"Error: Failed to parse JSON from '{input_file}': {e}", file=sys.stderr)
        sys.exit(1)

    simple: dict[str, str] = {}
    for key, value in enriched.items():
        if isinstance(value, dict):
            mot = value.get("mot")
            if mot:
                if mot in simple:
                    print(f"Warning: Duplicate entry for mot '{mot}', overwriting.")
                simple[mot] = key
            else:
                print(f"Warning: No 'mot' field for glyph '{key}', skipping.")
        elif isinstance(value, str):
            simple[key] = value
        else:
            print(f"Warning: Invalid value for key '{key}', skipping.")

    Path(output_file).write_text(json.dumps(simple, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Extraction terminée : '{output_file}' généré ({len(simple)} entrées).")


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Extract mot → glyphe mapping from enriched glyph_dict.json.")
    parser.add_argument('-i', '--input', default='glyph_dict.json', help='Chemin vers le fichier JSON source')
    parser.add_argument('-o', '--output', default='glyph_dict_simple.json', help='Chemin de sortie pour le mapping simple')
    args = parser.parse_args()
    extract(args.input, args.output)
 codex/supprimer-les-marqueurs-de-fusion-et-valider-les-fichiers

codex/finaliser-scripts-et-tests-de-compression

from .glyph_generator import _load_dict
import json

if __name__ == "__main__":
    d = _load_dict()
    print(json.dumps(d, indent=2, ensure_ascii=False))
 main
 main
