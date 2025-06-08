import os
import tempfile
import unittest
from pathlib import Path

from scripts.compressor import Compressor

class CompressorTest(unittest.TestCase):
    def setUp(self):
        # Crée un dossier temporaire isolé pour chaque test (mapping non persistant)
        self.tmp = tempfile.TemporaryDirectory()
        os.environ["GLYPH_DICT_PATH"] = str(Path(self.tmp.name) / "glyph_dict.json")

    def tearDown(self):
        self.tmp.cleanup()
        os.environ.pop("GLYPH_DICT_PATH", None)

    def test_visual_mode(self):
        comp = Compressor("visual")
        txt = "chat avec intelligence augmentée"
        compressed = comp.compress(txt)
        self.assertIsInstance(compressed, str)
        restored = comp.decompress(compressed)
        self.assertEqual(restored, txt)

    def test_abbrev_mode(self):
        comp = Compressor("abbrev")
        txt = "compression et décompression abbreviation abbreviation"
        compressed = comp.compress(txt)
        # Vérifie présence d'abréviation (premiers caractères)
        self.assertIn("abb", compressed)
        restored = comp.decompress(compressed)
        self.assertEqual(restored, txt)

    def test_alphanumeric_mode(self):
        comp = Compressor("alphanumeric")
        txt = "test alphanumérique token token"
        compressed = comp.compress(txt)
        self.assertIn("T", compressed)
        restored = comp.decompress(compressed)
        self.assertEqual(restored, txt)

    def test_custom_mode_existing_mapping(self):
        comp = Compressor("custom")
        # Prép: mapping manuel pour custom (pas d'ajout auto)
        comp.mapping = {"hello": "XX", "world": "YY"}
        comp._save_mapping()
        txt = "hello world"
        compressed = comp.compress(txt)
        self.assertIn("XX", compressed)
        self.assertIn("YY", compressed)
        restored = comp.decompress(compressed)
        self.assertEqual(restored, txt)

    def test_custom_mode_no_new_tokens(self):
        comp = Compressor("custom")
        # mapping volontairement vide
        txt = "nouveau mot"
        compressed = comp.compress(txt)
        # Aucun remplacement car pas de mapping connu
        self.assertEqual(compressed, txt)

if __name__ == "__main__":
    unittest.main()
