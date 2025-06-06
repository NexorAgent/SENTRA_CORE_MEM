import os
import tempfile
import unittest
import base64
import zlib
import json
import subprocess
import sys
from pathlib import Path

from scripts.glyph import glyph_generator as gg
from scripts.glyph import make_mem_block, decode_mem_block
from scripts.zmem_encoder import encode_zmem


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

    def test_mem_block_no_mapping(self):
        text = "cycle sans mapping"
        fields = {"ID": "ZTEST", "TS": "2025-01-01T00:00", "INT": "UTEST", "Σ": "MEM.GLYPH"}
        # ensure glyphs exist in dictionary
        gg.compress_text(text)
        block = make_mem_block(fields, text, include_mapping=False)
        restored = decode_mem_block(block)
        self.assertEqual(restored, text)

    def test_zmem_cycle(self):
        text = "texte pour zmem"
        zmem = Path(self.tmp.name) / "sample.zmem"
        src = Path(self.tmp.name) / "sample.src"
        ltxt = Path(self.tmp.name) / "sample.l64.t"
        lbin = Path(self.tmp.name) / "sample.l64.b"
        encode_zmem(
            content=text,
            ctx_tag="TEST",
            zlib_txt_out=str(ltxt),
            zlib_bin_out=str(lbin),
            zmem_src_out=str(src),
            zmem_bin_out=str(zmem),
            update_dict_path=str(Path(self.tmp.name) / "index.json"),
        )
        data = base64.b64decode(zmem.read_text())
        restored = zlib.decompress(data).decode("utf-8")
        self.assertEqual(restored, text)

    def test_batch_script(self):
        input_dir = Path(self.tmp.name) / "in"
        out_dir = Path(self.tmp.name) / "out"
        input_dir.mkdir()
        out_dir.mkdir()
        samples = {"a.txt": "bonjour monde", "b.txt": "deuxieme fichier"}
        for name, text in samples.items():
            (input_dir / name).write_text(text, encoding="utf-8")
        script = Path(__file__).resolve().parent / "scripts" / "batch_compress.py"
        subprocess.run([sys.executable, str(script), str(input_dir), str(out_dir)], check=True)
        report_file = out_dir / "compression_report.json"
        self.assertTrue(report_file.exists())
        report = json.loads(report_file.read_text())
        for name, original in samples.items():
            zpath = out_dir / f"{Path(name).stem}.zmem"
            data = base64.b64decode(zpath.read_text())
            restored = zlib.decompress(data).decode("utf-8")
            self.assertEqual(restored, original)
            self.assertIn(name, report)


if __name__ == "__main__":
    unittest.main()
