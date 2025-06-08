import os
import tempfile
import unittest
import subprocess
import sys
import base64
import zlib
import json
from pathlib import Path

from scripts.glyph import (
    glyph_generator as gg,
    make_mem_block,
    decode_mem_block,
    randomize_mapping,
    compress_with_dict,
)
from scripts import zmem_encoder
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
        gg.compress_text(text)  # ensure glyphs exist in dictionary
        block = make_mem_block(fields, text, include_mapping=False)
        restored = decode_mem_block(block)
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
