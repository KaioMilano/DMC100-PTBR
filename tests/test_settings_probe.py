import importlib.util
import os
from pathlib import Path
import unittest
from src.dmc100_ptbr.settings_probe import load_probe
from src.dmc100_ptbr.arm_dispatch import LANGUAGE


class SettingsProfileTests(unittest.TestCase):
    def test_unknown_image_rejected(self):
        with self.assertRaises(ValueError):
            load_probe(b"unknown",[0]*8)


ENGINES = all(importlib.util.find_spec(n) for n in ("unicorn","keystone"))


@unittest.skipUnless(ENGINES and os.environ.get("DMC100_V14_PATH"),"Private RAM decode opt-in")
class PrivateSettingsDecodeTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.path = Path(os.environ["DMC100_V14_PATH"])
        cls.data = cls.path.read_bytes()

    def test_all_language_bytes_are_copied_without_validation_in_this_stage(self):
        for language in range(256):
            result = load_probe(self.data,[0,language,22,33,44,55,66,77])
            self.assertEqual(result["decoded_bytes"],[language,44,22,33,55,66,77])
            self.assertEqual(set(result["writes"]),{(LANGUAGE+i,1) for i in range(7)})
            self.assertFalse(result["flash_executed"])
        self.assertEqual(self.path.read_bytes(),self.data)

    def test_halfword_high_bits_are_truncated_and_invalid_marker_is_rejected(self):
        result = load_probe(self.data,[0,0x1002,0xFFFF,3,4,5,6,7])
        self.assertEqual(result["decoded_bytes"],[2,4,255,3,5,6,7])
        with self.assertRaises(ValueError):
            load_probe(self.data,[1,2,3,4,5,6,7,8])
