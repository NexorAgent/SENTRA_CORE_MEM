import os
import tempfile
import unittest
import base64
import zlib
from pathlib import Path

from scripts.glyph import glyph_generator as gg
from scripts.glyph import make_mem_block, decode_mem_block

import sys
import types
sys.modules.setdefault("openai", types.ModuleType("openai"))
from scripts.project_resumer_gpt import compress_to_glyph
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

    def test_base64_round_trip(self):
        text = "contenu base64 compressé"
        compressed = compress_to_glyph(text)
        decoded = zlib.decompress(base64.b64decode(compressed)).decode("utf-8")
        self.assertEqual(decoded, text)

    def test_encode_zmem_round_trip(self):
        text = "texte mémoire zmem"
        out_dir = Path(self.tmp.name)
        encode_zmem(
            content=text,
            ctx_tag="TST",
            zlib_txt_out=str(out_dir / "t.l64.t"),
            zlib_bin_out=str(out_dir / "t.l64.b"),
            zmem_src_out=str(out_dir / "t.src"),
            zmem_bin_out=str(out_dir / "t.zmem"),
            update_dict_path=str(out_dir / "index.json"),
        )
        encoded = (out_dir / "t.zmem").read_text(encoding="utf-8")
        decoded = zlib.decompress(base64.b64decode(encoded)).decode("utf-8")
        self.assertEqual(decoded, text)

    def test_batch_compression_directory(self):
        batch_dir = Path(self.tmp.name) / "batch"
        out_dir = Path(self.tmp.name) / "out"
        batch_dir.mkdir()
        out_dir.mkdir()
        samples = {
            "a.txt": "alpha",
            "b.txt": "beta",
            "c.txt": "gamma",
        }
        for fname, content in samples.items():
            (batch_dir / fname).write_text(content, encoding="utf-8")

        for fname, content in samples.items():
            encode_zmem(
                content=content,
                ctx_tag=fname,
                zlib_txt_out=str(out_dir / f"{fname}.l64.t"),
                zlib_bin_out=str(out_dir / f"{fname}.l64.b"),
                zmem_src_out=str(out_dir / f"{fname}.src"),
                zmem_bin_out=str(out_dir / f"{fname}.zmem"),
                update_dict_path=str(out_dir / "index.json"),
            )

        for fname, original in samples.items():
            encoded = (out_dir / f"{fname}.zmem").read_text(encoding="utf-8")
            decoded = zlib.decompress(base64.b64decode(encoded)).decode("utf-8")
            self.assertEqual(decoded, original)


if __name__ == "__main__":
    unittest.main()
