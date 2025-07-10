import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from scripts.glyph.compressor import Compressor


class CompressorTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.dict_path = Path(self.tmp.name) / "glyph.json"
        os.environ["GLYPH_DICT_PATH"] = str(self.dict_path)

    def tearDown(self):
        self.tmp.cleanup()
        os.environ.pop("GLYPH_DICT_PATH", None)

    def test_abbrev_cycle(self):
        c = Compressor(mode="abbrev")
        text = "memoire compression unique"
        compressed = c.compress(text)
        self.assertNotEqual(compressed, text)
        restored = c.decompress(compressed)
        self.assertEqual(restored, text)

    def test_cli_usage(self):
        input_file = Path(self.tmp.name) / "input.txt"
        output_file = Path(self.tmp.name) / "out.txt"
        input_file.write_text("memo block universel", encoding="utf-8")

        subprocess.run(
            [
                sys.executable,
                "-m",
                "scripts.glyph.compressor",
                "--mode",
                "abbrev",
                str(input_file),
                str(output_file),
            ],
            check=True,
        )

        out_text = output_file.read_text(encoding="utf-8")
        c = Compressor(mode="abbrev")
        self.assertEqual(c.decompress(out_text), "memo block universel")


if __name__ == "__main__":
    unittest.main()
