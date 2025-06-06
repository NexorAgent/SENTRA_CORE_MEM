import os
import tempfile
import unittest
from pathlib import Path

from scripts.glyph import glyph_generator as gg
from scripts.glyph import make_mem_block, decode_mem_block, Compressor
import subprocess
import json
import sys


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

    def test_compressor_modes(self):
        text = "exemple de texte compressable"
        for mode in [Compressor.GLYPH, Compressor.ZLIB, Compressor.BOTH]:
            with self.subTest(mode=mode):
                comp = Compressor(mode)
                data = comp.compress(text)
                self.assertEqual(comp.decompress(data), text)

    def _run_cli(self, mode: str):
        workdir = Path(self.tmp.name) / f"data_{mode}"
        workdir.mkdir()
        originals = []
        for i in range(3):
            p = workdir / f"file{i}.txt"
            content = f"ligne {i} pour {mode}"
            p.write_text(content, encoding="utf-8")
            originals.append((p, content))

        cmd = [sys.executable, "-m", "scripts.glyph.batch_cli", mode, str(workdir)]
        subprocess.run(cmd, check=True)

        report_path = workdir / "compression_report.json"
        self.assertTrue(report_path.exists())
        report = json.loads(report_path.read_text(encoding="utf-8"))
        for src, content in originals:
            dec_file = Path(report[str(src)]["decompressed"])
            self.assertEqual(dec_file.read_text(encoding="utf-8"), content)

    def test_batch_cli_all_modes(self):
        for mode in [Compressor.GLYPH, Compressor.ZLIB, Compressor.BOTH]:
            with self.subTest(mode=mode):
                self._run_cli(mode)


if __name__ == "__main__":
    unittest.main()
