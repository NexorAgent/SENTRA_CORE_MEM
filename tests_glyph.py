import os
import tempfile
import unittest
import subprocess
import sys
import base64
import zlib
from pathlib import Path

from scripts.glyph import glyph_generator as gg
from scripts.glyph import make_mem_block, decode_mem_block
from scripts import zmem_encoder


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

    def test_zmem_encoder_cycle(self):
        text = "compression zmem locale"
        base = Path(self.tmp.name)
        zlib_txt = base / "out.l64.t"
        zlib_bin = base / "out.l64.b"
        zmem_src = base / "out.src"
        zmem_bin = base / "out.zmem"
        index = base / "index.json"

        zmem_encoder.encode_zmem(
            content=text,
            ctx_tag="TCTX",
            zlib_txt_out=str(zlib_txt),
            zlib_bin_out=str(zlib_bin),
            zmem_src_out=str(zmem_src),
            zmem_bin_out=str(zmem_bin),
            update_dict_path=str(index),
        )

        decoded = zlib.decompress(base64.b64decode(zmem_bin.read_text())).decode("utf-8")
        self.assertEqual(decoded, text)
        if zlib_bin.exists():
            decoded2 = zlib.decompress(zlib_bin.read_bytes()).decode("utf-8")
            self.assertEqual(decoded2, text)

    def test_batch_cli_outputs(self):
        sample = "<note>demo de batch</note>"
        input_path = Path(self.tmp.name) / "sample.txt"
        input_path.write_text(sample, encoding="utf-8")
        script = Path(__file__).resolve().parent / "scripts" / "run_auto_translator.py"
        result = subprocess.run(
            [sys.executable, str(script), "-i", str(input_path)],
            cwd=self.tmp.name,
            capture_output=True,
            text=True,
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("Pipeline complet exécuté", result.stdout)

        out_txt = Path(self.tmp.name) / f"{input_path.stem}.zlib.txt"
        out_bin = Path(self.tmp.name) / f"{input_path.stem}.zlib"
        zmem_src = Path(self.tmp.name) / "memory_zia" / "sentra_memory.zmem.src"
        zmem_bin = Path(self.tmp.name) / "memory_zia" / "sentra_memory.zmem"
        dict_file = Path(self.tmp.name) / "memory_zia" / "mem_dict.json"

        for f in (out_txt, out_bin, zmem_src, zmem_bin, dict_file):
            self.assertTrue(f.exists(), f"Missing {f}")

        comp_txt = out_txt.read_text(encoding="utf-8")
        self.assertEqual(zlib.decompress(out_bin.read_bytes()).decode("utf-8"), comp_txt)
        self.assertEqual(
            zlib.decompress(base64.b85decode(zmem_bin.read_bytes())).decode("utf-8"),
            zmem_src.read_text(encoding="utf-8"),
        )


if __name__ == "__main__":
    unittest.main()
