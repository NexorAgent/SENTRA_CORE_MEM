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

