import hashlib
import unittest

from src.dmc100_ptbr.catalog import COMMUNITY_REPORTED_V14_SIZE, STRINGS
from src.dmc100_ptbr.inspect import inspect_bytes


class ReadOnlyInspectionTests(unittest.TestCase):
    def test_empty_firmware_reports_no_matches(self):
        report = inspect_bytes(b"")
        self.assertEqual(report["bytes"], 0)
        self.assertEqual(report["matches"], 0)
        self.assertFalse(report["reported_size_matches"])
        self.assertEqual(report["sha256"], hashlib.sha256(b"").hexdigest())

    def test_synthetic_data_matches_catalog(self):
        # Synthetic fixture, never an actual installable firmware.
        fake = bytearray(COMMUNITY_REPORTED_V14_SIZE)
        for offset, original, _ in STRINGS:
            fake[offset : offset + len(original)] = original.encode("ascii")
        before = bytes(fake)
        report = inspect_bytes(before, "synthetic-fixture")
        self.assertEqual(report["matches"], len(STRINGS))
        self.assertTrue(report["reported_size_matches"])
        self.assertEqual(before, bytes(fake), "Inspection changed input bytes")

    def test_byte_mismatch_is_detected(self):
        fake = bytearray(COMMUNITY_REPORTED_V14_SIZE)
        for offset, original, _ in STRINGS:
            fake[offset : offset + len(original)] = original.encode("ascii")
        fake[STRINGS[0][0]] = ord("X")
        report = inspect_bytes(bytes(fake))
        self.assertEqual(report["matches"], len(STRINGS) - 1)
        self.assertFalse(report["strings"][0]["matches"])


if __name__ == "__main__":
    unittest.main()
