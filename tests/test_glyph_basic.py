import os
import pathlib
import tempfile
from scripts.glyph import glyph_generator as gg


def setup_module(module):
    module.tmp = tempfile.TemporaryDirectory()
    os.environ["GLYPH_DICT_PATH"] = str(pathlib.Path(module.tmp.name) / "glyph.json")


def teardown_module(module):
    module.tmp.cleanup()
    os.environ.pop("GLYPH_DICT_PATH", None)


def test_round_trip():
    text = "compression glyphique test"
    compressed = gg.compress_text(text)
    assert gg.decompress_text(compressed) == text


def test_obfuscation_cycle():
    text = "secret memo unique"
    compressed, mapping = gg.compress_text(text, obfuscate=True)
    restored = gg.decompress_with_dict(compressed, mapping)
    assert restored == text
