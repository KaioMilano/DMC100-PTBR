import importlib.util
import os
from pathlib import Path
import unittest

from src.dmc100_ptbr.original_menu import compare, run_menu
from src.dmc100_ptbr.v14 import LOAD_BASE


class OriginalMenuProfileTests(unittest.TestCase):
    def test_unknown_image_rejected_before_execution(self):
        with self.assertRaises(ValueError):
            run_menu(b"not firmware", 2)


ENGINES = all(importlib.util.find_spec(n) for n in ("unicorn", "keystone"))


@unittest.skipUnless(ENGINES and os.environ.get("DMC100_V14_PATH"), "Private opt-in original menu test")
class PrivateOriginalMenuTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.path = Path(os.environ["DMC100_V14_PATH"])
        cls.data = cls.path.read_bytes()

    def test_third_value_still_runs_english_two_choice_layout(self):
        report = compare(self.data)
        self.assertTrue(report["ptbr_byte_matches_english_trace"])
        self.assertTrue(report["invalid_byte_matches_english_trace"])
        self.assertTrue(report["chinese_differs_from_english"])
        self.assertEqual(set(report["text_calls_per_locale"].values()), {3})
        self.assertFalse(report["third_option_in_original_menu"])
        self.assertFalse(report["firmware_generated"])
        self.assertEqual(self.path.read_bytes(), self.data)

    def test_original_menu_text_positions_and_font_arguments(self):
        result = run_menu(self.data, 1)
        texts = [t for t in result["trace"] if t["call"] == "text"]
        self.assertEqual([(t["args"][0], t["args"][1]) for t in texts],
                         [(93, 158), (106, 203), (106, 244)])
        self.assertEqual([t["args"][2] - LOAD_BASE for t in texts], [0x5A44, 0x5A50, 0x5A5C])
        self.assertTrue(all(t["stack_args"][1:] == [16, 1] for t in texts))
