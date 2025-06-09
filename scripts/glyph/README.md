# Glyph Translation Environment

This folder provides a minimal environment for managing compressed glyph
representations. It can be integrated in a larger IA project such as
`SENTRA_CORE_MEM`.

## Modules

- `glyph_generator.py` – handles term ↔ glyph mapping. New glyphs are
  created on demand and stored in `memory/glyph_dict.json`.
- `glyph_watcher.py` – utilities to scan log directories and register new
  terms automatically.
- `extract_glyph_dict.py` – print the current dictionary.
- `clean_glyph_dict.py` – remove duplicated glyph entries.
<<<<<<< HEAD
- `mem_block.py` – build and decode universal MEM.BLOCK strings.
=======
>>>>>>> 228a3aa670cbfd79800f8695cad5281122fe07c4

A persistent dictionary file `memory/glyph_dict.json` is required. The path
can be overridden via the `GLYPH_DICT_PATH` environment variable.

<<<<<<< HEAD
## Multi‑mode Compression

The compression pipeline works in two stages:

1. **Glyph substitution** – frequent terms are replaced by short symbols
   defined in `glyph_dict.json`.
2. **Binary compression** – the glyphified text is compressed with zlib and
   encoded using base85.  This payload is stored under the `CMPZ` field of a
   MEM.BLOCK.

The environment also supports a *plain* mode (glyphs only) for debugging by
setting `GLYPH_MODE=plain` before executing the tools.

### Obfuscation

Because both the glyph substitution and binary compression are reversible, the
resulting MEM.BLOCK is human‑readable only after decoding.  This lightweight
obfuscation prevents casual inspection of the stored logs while keeping the
process deterministic.

## Batch CLI

The helper scripts can be invoked directly from the command line:

```bash
# scan a log directory and update the dictionary
python -c "from scripts.glyph.glyph_watcher import scan_directory; scan_directory('logs')"

# inspect or clean the dictionary
python scripts/glyph/extract_glyph_dict.py
python scripts/glyph/clean_glyph_dict.py
```

These commands make it easy to batch‑register terms and keep the mapping tidy.

## Adding New Glyph Sets

Glyphs are stored in `memory/glyph_dict.json`.  To add a new set, simply
pre‑populate this file with key/value pairs or run the watcher on a corpus of
text files.  The generator will avoid collisions and append missing terms
automatically.

## Synchronizing Dictionaries

When multiple agents share memory, copy `glyph_dict.json` between instances so
that compression and decompression remain consistent.  The dictionary path can
be configured on each agent via the `GLYPH_DICT_PATH` environment variable.

=======
>>>>>>> 228a3aa670cbfd79800f8695cad5281122fe07c4
## Usage Example

```python
from scripts.glyph.glyph_generator import compress_text, decompress_text

text = "Les agents analysent les logs"
compressed = compress_text(text)
print(compressed)
print(decompress_text(compressed))
```

<<<<<<< HEAD
## Adding New Glyph Sets

1. Create a new JSON dictionary such as `memory/glyph_dict_custom.json`.
2. Set the environment variable `GLYPH_DICT_PATH` to this file.
3. Use `glyph_watcher.py` or `pipeline_traducteur.py` to populate it.

## Sharing the Dictionary

All agents read from the path given in `GLYPH_DICT_PATH`. Point this variable
to a common location (network share or repository) so every agent uses the same
mapping table.

## Backup and Versioning

Commit `glyph_dict.json` to Git and keep a compressed copy with:
`gzip -k memory/glyph_dict.json`. Archiving the dictionary preserves its
evolution and can slightly improve compression over time.

## Obfuscation Mode

Pass `include_mapping=False` to `make_mem_block()` to omit the glyph table.
Only agents with the dictionary will be able to decode the block.

=======
>>>>>>> 228a3aa670cbfd79800f8695cad5281122fe07c4
## Tests

A suite `tests_glyph.py` uses `unittest` to verify that compressing then
 decompressing strings yields the original text.
<<<<<<< HEAD

## MEM.BLOCK Workflow

`make_mem_block()` creates a compressed block that can be decoded
anywhere, even without the glyph dictionary. Use `include_mapping=True`
to append the mapping table so a GPT agent can restore the text.

Example with the mapping table appended:

```
⦿MEM.BLOCK🧠∴⟁ID⟶ZCORE↯⟁TS⟶2025.05.29T18:00↯⟁INT⟶TEST.TRADUCTION↯⟁Σ⟶MEM.GLYPH++↯⟁CMPZ⟶ƛ:Gz85#abc123...↯⟁SEAL⟶✅SENTRA
{"chat": "⊚3", "analyse": "@a"}
```

### Obfuscation Mode

Calling the compressor with `--obfuscate` assigns random glyphs instead of the
persistent dictionary. The temporary mapping is written to `obfuscated_map.json`
(or the path provided with `--map-out`). Decryption simply loads this mapping and
passes it to `decompress_with_dict()`:

```python
from scripts.glyph.glyph_generator import compress_text, decompress_with_dict
import json

compressed = compress_text("texte secret", obfuscate=True, mapping_file="map.json")
mapping = json.load(open("map.json", "r", encoding="utf-8"))
original = decompress_with_dict(compressed, mapping)
```

This feature only obscures content. It is *not* strong encryption—frequency
analysis of the glyphs could reveal common terms—so keep the mapping file safe
if confidentiality matters.

=======
>>>>>>> 228a3aa670cbfd79800f8695cad5281122fe07c4
