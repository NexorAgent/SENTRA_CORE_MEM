import tempfile
import unittest
from pathlib import Path

from fastapi.testclient import TestClient

from scripts import file_manager
from scripts.api_sentra import app


class FileManagerTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        file_manager.LOG_FILE = Path(self.tmp.name) / "actions.log"
        self.client = TestClient(app)

    def tearDown(self):
        self.tmp.cleanup()

    def test_delete_move_archive(self):
        f1 = Path(self.tmp.name) / "del.txt"
        f1.write_text("data")
        self.assertTrue(file_manager.delete_file(f1))
        self.assertFalse(f1.exists())

        src = Path(self.tmp.name) / "src.txt"
        src.write_text("hi")
        dst = Path(self.tmp.name) / "dst.txt"
        self.assertTrue(file_manager.move_file(src, dst))
        self.assertFalse(src.exists())
        self.assertTrue(dst.exists())

        to_arch = Path(self.tmp.name) / "arc.txt"
        to_arch.write_text("z")
        arch_dir = Path(self.tmp.name) / "arch"
        self.assertTrue(file_manager.archive_file(to_arch, arch_dir))
        self.assertFalse(to_arch.exists())
        self.assertTrue((arch_dir / "arc.txt").exists())

    def test_api_endpoints(self):
        p = Path(self.tmp.name) / "file.txt"
        p.write_text("x")
        res = self.client.post("/delete_file", json={"path": str(p)})
        self.assertEqual(res.status_code, 200)
        self.assertFalse(p.exists())

        s = Path(self.tmp.name) / "m1.txt"
        s.write_text("a")
        d = Path(self.tmp.name) / "m2.txt"
        res = self.client.post("/move_file", json={"src": str(s), "dst": str(d)})
        self.assertEqual(res.status_code, 200)
        self.assertTrue(d.exists())

        f = Path(self.tmp.name) / "ar.txt"
        f.write_text("b")
        ad = Path(self.tmp.name) / "arcdir"
        res = self.client.post(
            "/archive_file", json={"path": str(f), "archive_dir": str(ad)}
        )
        self.assertEqual(res.status_code, 200)
        self.assertTrue((ad / "ar.txt").exists())


if __name__ == "__main__":
    unittest.main()
