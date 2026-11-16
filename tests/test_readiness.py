import contextlib
import io
import json
from pathlib import Path
import tempfile
import unittest

from src.dmc100_ptbr.readiness import assess_bytes, main, resource_inventory, resource_requirements


class ReadinessTests(unittest.TestCase):
    def test_unknown_fingerprint_never_gets_fixed_address_profile(self):
        report = assess_bytes(b"not an original firmware")
        self.assertFalse(report["profile_applied"])
        self.assertFalse(report["installable_ready"])
        self.assertNotIn("settings", report)

    def test_paths_require_nul_known_family_and_no_traversal(self):
        data = (b"2:/UI/mode/V.jpg\0" + b"2:/UI/mode/V.jpg\0" +
                b"2:/UI/mode/../secret.jpg\0" + b"2:/UI/other/private.jpg\0" +
                b"2:/UI/mode/not-terminated.jpg!")
        self.assertEqual(resource_requirements(data), {"mode/V.jpg"})

    def test_inventory_counts_only_requested_local_files_and_never_changes_them(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "mode").mkdir()
            image = root / "mode/V.jpg"
            content = b"\xff\xd8synthetic-not-a-real-jpeg\xff\xd9"
            image.write_bytes(content)
            (root / "private.txt").write_text("CONFIDENTIAL")
            report = resource_inventory({"mode/V.jpg", "mode/A.jpg"}, root)
            self.assertEqual(report["present"], 1)
            self.assertEqual(report["minimal_jpeg_signatures"], 1)
            self.assertEqual(report["missing"], ["mode/A.jpg"])
            self.assertNotIn("CONFIDENTIAL", json.dumps(report))
            self.assertEqual(image.read_bytes(), content)

    def test_html_renamed_as_jpeg_is_not_counted_as_jpeg_signature(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "mode").mkdir()
            (root / "mode/V.jpg").write_text("<html>error</html>")
            report = resource_inventory({"mode/V.jpg"}, root)
            self.assertEqual(report["present"], 1)
            self.assertEqual(report["minimal_jpeg_signatures"], 0)

    def test_missing_directory_does_not_imply_complete_resources(self):
        report = resource_inventory({"mode/V.jpg"}, None)
        self.assertFalse(report["supplied"])
        self.assertEqual(report["present"], 0)
        self.assertEqual(report["missing"], ["mode/V.jpg"])

    def test_inventory_rejects_unsafe_requirements(self):
        with self.assertRaises(ValueError):
            resource_inventory({"../secret.jpg"}, None)

    def test_cli_blocked_exit_and_no_output_firmware(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            firmware = root / "synthetic.bin"
            firmware.write_bytes(b"synthetic")
            with contextlib.redirect_stdout(io.StringIO()) as output:
                self.assertEqual(main([str(firmware)]), 1)
            self.assertFalse(json.loads(output.getvalue())["firmware_generated"])
            self.assertEqual(list(root.iterdir()), [firmware])
