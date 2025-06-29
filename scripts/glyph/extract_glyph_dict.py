#!/usr/bin/env python3
"""
extract_glyph_dict.py

Script to extract a simple mapping mot → glyphe from an enriched glyph_dict.json
format (glyph as key, info dict as value), and output glyph_dict_simple.json.
"""
import json
import argparse
import sys

def extract(input_file: str, output_file: str) -> None:
    # Load the enriched glyph dictionary
    try:
        with open(input_file, 'r', encoding='utf-8') as f:
            enriched = json.load(f)
    except FileNotFoundError:
        print(f"Error: Input file '{input_file}' not found.", file=sys.stderr)
        sys.exit(1)
    except json.JSONDecodeError as e:
        print(f"Error: Failed to parse JSON from '{input_file}': {e}", file=sys.stderr)
        sys.exit(1)

    simple: dict[str, str] = {}
    for glyph, info in enriched.items():
        mot = info.get('mot')
        if mot:
            # If duplicated mots, last wins or could warn
            if mot in simple:
                print(f"Warning: Duplicate entry for mot '{mot}', overwriting.")
            simple[mot] = glyph
        else:
            print(f"Warning: No 'mot' field for glyph '{glyph}', skipping.")

    # Write the simple mapping to output file
    try:
        with open(output_file, 'w', encoding='utf-8') as f_out:
            json.dump(simple, f_out, ensure_ascii=False, indent=2)
    except IOError as e:
        print(f"Error: Could not write to '{output_file}': {e}", file=sys.stderr)
        sys.exit(1)

    print(f"Extraction terminée : '{output_file}' généré ({len(simple)} entrées).")

if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description="Extract mot → glyphe mapping from enriched glyph_dict.json."
    )
    parser.add_argument(
        '-i', '--input', default='glyph_dict.json',
        help='Chemin vers le fichier JSON enrichi (défaut: glyph_dict.json)'
    )
    parser.add_argument(
        '-o', '--output', default='glyph_dict_simple.json',
        help='Chemin de sortie pour le mapping simple (défaut: glyph_dict_simple.json)'
    )
    args = parser.parse_args()
    extract(args.input, args.output)
from .glyph_generator import _load_dict
import json

if __name__ == "__main__":
    d = _load_dict()
    print(json.dumps(d, indent=2, ensure_ascii=False))
