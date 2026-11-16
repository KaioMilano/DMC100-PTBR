import hashlib
import json
from pathlib import Path
import re
import tempfile
import unittest
import zipfile

from src.dmc100_ptbr.preview_package import ASSETS, build

ROOT = Path(__file__).resolve().parents[1]


class PreviewPackageTests(unittest.TestCase):
    def test_archive_has_complete_local_assets_and_valid_manifest(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "preview.zip"
            build(ROOT, path)
            with zipfile.ZipFile(path) as archive:
                names = set(archive.namelist())
                self.assertEqual(names, {"ABRIR.html", "LICENSE", "manifest.json"}
                                 | {"simulator/" + name for name in ASSETS})
                manifest = json.loads(archive.read("manifest.json"))
                self.assertFalse(manifest["firmware_included"])
                for name, expected in manifest["files"].items():
                    self.assertEqual(hashlib.sha256(archive.read(name)).hexdigest(), expected)
                    if name.endswith(".html"):
                        for ref in re.findall(r'(?:src|href)="([^"]+)"', archive.read(name).decode()):
                            if ref.startswith(("data:", "#")):
                                continue
                            self.assertNotIn("://", ref)
                            self.assertIn(str(Path(name).parent.joinpath(ref)).replace("\\", "/"), names)

    def test_package_is_reproducible(self):
        with tempfile.TemporaryDirectory() as tmp:
            first, second = Path(tmp) / "a.zip", Path(tmp) / "b.zip"
            build(ROOT, first)
            build(ROOT, second)
            self.assertEqual(first.read_bytes(), second.read_bytes())

    def test_missing_assets_fail_without_partial_output(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "preview.zip"
            with self.assertRaises(FileNotFoundError):
                build(Path(tmp) / "absent", path)
            self.assertFalse(path.exists())
