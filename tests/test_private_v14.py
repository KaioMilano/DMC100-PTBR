"""Opt-in read-only integration checks; never download or include a firmware.

Set DMC100_V14_PATH to the privately obtained file. CI skips these checks.
"""
import hashlib
import os
from pathlib import Path
import unittest

from src.dmc100_ptbr.analyze import analyze_bytes


@unittest.skipUnless(os.environ.get("DMC100_V14_PATH"), "Private V1.4 not supplied")
class PrivateV14Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.path = Path(os.environ["DMC100_V14_PATH"])
        cls.data = cls.path.read_bytes()
        cls.report = analyze_bytes(cls.data)

    def test_download_identity_and_vectors(self):
        self.assertEqual(len(self.data), 95984)
        self.assertEqual(hashlib.sha256(self.data).hexdigest(),
                         "f8eab197553e117a374dc9926989b8ec2105baa8120682bd5c864bda30e8364d")
        self.assertEqual(self.report["vectors_candidate"]["initial_sp_hex"], "0x20007240")
        self.assertEqual(self.report["vectors_candidate"]["reset_hex"], "0x0800721D")

    def test_strings_offsets_and_duplicates(self):
        self.assertEqual(self.report["nul_terminated_matches"], 14)
        language = next(i for i in self.report["strings"] if i["original"] == "Language")
        self.assertEqual(language["occurrences"], [0x5A44, 0x6150])
        self.assertEqual(self.data[0x58FF], 32)
        self.assertEqual(self.data[0xB28F], 32)

    def test_font_profile_and_original_unchanged(self):
        profile = self.report["observed_v14_profile"]
        self.assertTrue(profile["applied"])
        self.assertEqual(profile["reset_file_offset"], 0x21C)
        self.assertEqual(len(profile["tables"]), 8)
        self.assertTrue(all(t["in_bounds"] for t in profile["tables"]))
        self.assertEqual(profile["tables"][0]["offset"], 0xF17A)
        self.assertEqual(profile["tables"][-1]["end_exclusive"], 0x14888)
        self.assertTrue(all(not t["requested_accent_coverage"]["utf-8"]
                            for t in profile["tables"] if t["kind"] == "paired"))
        self.assertEqual(hashlib.sha256(self.path.read_bytes()).digest(),
                         hashlib.sha256(self.data).digest())
