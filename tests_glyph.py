import os
import tempfile
import unittest
from pathlib import Path

from scripts.glyph import (
    glyph_generator as gg,
    make_mem_block,
    decode_mem_block,
    decompress_with_dict,
)


class GlyphRoundTripTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.dict_path = Path(self.tmp.name) / "glyph.json"
        os.environ["GLYPH_DICT_PATH"] = str(self.dict_path)

    def tearDown(self):
        self.tmp.cleanup()
        os.environ.pop("GLYPH_DICT_PATH", None)

    def test_round_trip(self):
        samples = [
            "chat avec intelligence", "analyse des données", "production de rapport",
            "mémoire active", "programme modulaire", "réseau neuronal",
            "système autonome", "compression glyphique", "gestion de projet",
            "supervision automatique", "pipeline de tests", "nettoyage mémoire",
            "extraction dictionnaire", "audit de collisions", "surveillance logs",
            "génération de glyphes", "interaction utilisateur", "réponse adaptative",
            "optimisation code", "lecture configuration"
        ]
        for text in samples:
            compressed = gg.compress_text(text)
            restored = gg.decompress_text(compressed)
            self.assertEqual(restored, text)

    def test_mem_block_cycle(self):
        text = "memo block universel"
        fields = {"ID": "ZTEST", "TS": "2025-01-01T00:00", "INT": "UTEST", "Σ": "MEM.GLYPH"}
        block = make_mem_block(fields, text, include_mapping=True)
        restored = decode_mem_block(block)
        self.assertEqual(restored, text)

    def test_obfuscate_mode(self):
        text = "obfuscation unique test"
        compressed, mapping = gg.compress_text(text, obfuscate=True)
        self.assertIsInstance(mapping, dict)
        restored = decompress_with_dict(compressed, mapping)
        self.assertEqual(restored, text)


if __name__ == "__main__":
    unittest.main()
