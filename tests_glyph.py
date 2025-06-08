import os
import tempfile
import unittest
import subprocess
import sys
import base64
import zlib
import json
from pathlib import Path
import types

from scripts.glyph import (
    glyph_generator as gg,
    make_mem_block,
    decode_mem_block,
    randomize_mapping,
    compress_with_dict,
    decompress_with_dict,
)
from scripts.compressor import Compressor
from scripts import zmem_encoder
from scripts.zmem_encoder import encode_zmem

# Mock openai if not installed, for scripts.project_resumer_gpt
sys.modules.setdefault("openai", types.ModuleType("openai"))
try:
    from scripts.project_resumer_gpt import compress_to_glyph
except ImportError:
    compress_to_glyph = None

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
        gg.compress_text(text)  # ensure glyphs exist in dictionary
        block = make_mem_block(fields, text, include_mapping=False)
        restored = decode_mem_block(block)
        self.assertEqual(restored, text)

    def test_obfuscate_mode(self):
        text = "obfuscation unique test"
        compressed, mapping = gg.compress_text(text, obfuscate=True)
        self.assertIsInstance(mapping, dict)
        restored = decompress_with_dict(compressed, mapping)
        self.assertEqual(restored, text)

    def test_obfuscate_cycle(self):
        text = "secret memo"
        base_mapping = {"secret": "AA", "memo": "BB"}
        obf_mapping = randomize_mapping(base_mapping)
        compressed = compress_with_dict(text, obf_mapping)
        restored = gg.decompress_with_dict(compressed, obf_mapping)
        self.assertEqual(restored, text)

    def test_obfuscation_cycle(self):
        text = "secret message"
        map_path = Path(self.tmp.name) / "obf.json"
        compressed = gg.compress_text(text, obfuscate=True, mapping_file=map_path)
        mapping = json.loads(map_path.read_text(encoding="utf-8"))
        restored = gg.decompress_with_dict(compressed, mapping)
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

    def test_base64_round_trip(self):
        if compress_to_glyph is None:
            self.skipTest("compress_to_glyph unavailable (project_resumer_gpt missing)")
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

    def test_compressor_all_modes(self):
        txt = "test unitaire pour tous les modes compressor compressor"
        for mode in ["visual", "abbrev", "alphanumeric", "custom"]:
            with self.subTest(mode=mode):
                comp = Compressor(mode)
                if mode == "custom":
                    comp.mapping = {"test": "X1", "unitaire": "Y2", "pour": "Z3", "tous": "A4", "les": "B5", "modes": "C6", "compressor": "C7"}
                    comp._save_mapping()
                compressed = comp.compress(txt)
                decompressed = comp.decompress(compressed)
                self.assertEqual(decompressed, txt)

class BatchCompressTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.src = Path(self.tmp.name) / "src"
        self.dst = Path(self.tmp.name) / "dst"
        self.src.mkdir()
        (self.src / "a.txt").write_text("bonjour monde", encoding="utf-8")
        sub = self.src / "sub"
        sub.mkdir()
        (sub / "b.txt").write_text("autre fichier", encoding="utf-8")
        self.dict_path = Path(self.tmp.name) / "glyph.json"
        os.environ["GLYPH_DICT_PATH"] = str(self.dict_path)

    def tearDown(self):
        self.tmp.cleanup()
        os.environ.pop("GLYPH_DICT_PATH", None)

    def test_batch_compress(self):
        from scripts.glyph.batch_compress import compress_directory
        report = compress_directory(self.src, self.dst, mode="csv", obfuscate=False)
        self.assertTrue((self.dst / "a.txt.mb").exists())
        self.assertTrue((self.dst / "sub" / "b.txt.mb").exists())
        self.assertTrue(report.exists())

if __name__ == "__main__":
    unittest.main()
