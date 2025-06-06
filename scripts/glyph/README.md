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
- `mem_block.py` – build and decode universal MEM.BLOCK strings.

A persistent dictionary file `memory/glyph_dict.json` is required. The path
can be overridden via the `GLYPH_DICT_PATH` environment variable.

## Usage Example

```python
from scripts.glyph.glyph_generator import compress_text, decompress_text

text = "Les agents analysent les logs"
compressed = compress_text(text)
print(compressed)
print(decompress_text(compressed))
```

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

## Tests

A suite `tests_glyph.py` uses `unittest` to verify that compressing then
 decompressing strings yields the original text.

## MEM.BLOCK Workflow

`make_mem_block()` creates a compressed block that can be decoded
anywhere, even without the glyph dictionary. Use `include_mapping=True`
to append the mapping table so a GPT agent can restore the text.

Example block taken from `logs/tets/test_log_translated.txt`:

```
⦿MEM.BLOCK🧠∴⟁ID⟶ZCORE↯⟁TS⟶2025.05.29T18:00↯⟁INT⟶TEST.TRADUCTION↯⟁Σ⟶MEM.GLYPH++↯⟁CMPZ⟶ƛ:Gz85#abc123...↯⟁SEAL⟶✅SENTRA
```

