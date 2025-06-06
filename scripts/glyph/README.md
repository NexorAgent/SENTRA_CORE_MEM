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

## Tests

A suite `tests_glyph.py` uses `unittest` to verify that compressing then
 decompressing strings yields the original text.
