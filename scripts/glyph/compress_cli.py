#!/usr/bin/env python3
"""CLI pour compresser un fichier texte en MEM.BLOCK (glyphique)."""

import argparse
import json
from pathlib import Path

from .mem_block import make_mem_block


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Compresse un texte en MEM.BLOCK glyphique (avec ou sans mapping, obfuscation possible)"
    )
    parser.add_argument("input", help="Fichier texte source")
    parser.add_argument(
        "-o", "--output", required=True, help="Fichier destination pour le MEM.BLOCK"
    )
    parser.add_argument("--id", default="ZCLI", help="Champ ID pour le bloc")
    parser.add_argument(
        "--obfuscate",
        action="store_true",
        help="Obfusque les glyphes (randomise les tokens)",
    )
    parser.add_argument("--mapping-out", help="Chemin où sauvegarder le mapping (JSON)")
    args = parser.parse_args()

    text = Path(args.input).read_text(encoding="utf-8")
    fields = {"ID": args.id, "TS": "", "INT": "CLI", "Σ": "MEM.GLYPH"}

    if args.obfuscate:
        block, mapping = make_mem_block(fields, text, obfuscate=True)
        Path(args.output).write_text(block, encoding="utf-8")
        if args.mapping_out:
            Path(args.mapping_out).write_text(
                json.dumps(mapping, ensure_ascii=False, indent=2), encoding="utf-8"
            )
        print(f"Wrote MEM.BLOCK to {args.output}")
        print(f"Mapping saved to {args.mapping_out}" if args.mapping_out else "")
    else:
        include = args.mapping_out is not None
        block = make_mem_block(fields, text, include_mapping=include)
        Path(args.output).write_text(block, encoding="utf-8")
        if args.mapping_out and include:
            # Si mapping inclus dans le bloc, extraire le mapping du bloc
            try:
                _header, mapping_json = block.split("\n", 1)
                mapping = json.loads(mapping_json)
                Path(args.mapping_out).write_text(
                    json.dumps(mapping, ensure_ascii=False, indent=2), encoding="utf-8"
                )
                print(f"Mapping saved to {args.mapping_out}")
            except Exception:
                print("[WARN] Impossible d’extraire le mapping du bloc généré.")
        print(f"Wrote MEM.BLOCK to {args.output}")


if __name__ == "__main__":
    main()
