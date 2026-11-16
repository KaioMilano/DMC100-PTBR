"""Synthetic ARM tests are public. Real-image tests are explicit opt-in only."""
import importlib.util
import os
from pathlib import Path
import struct
import unittest

from src.dmc100_ptbr.arm_dispatch import (DATA, STACK, TEXT, PROTECTED, assemble,
                                         compare_private, payload, private_mappings, run)
from src.dmc100_ptbr.catalog import STRINGS
from src.dmc100_ptbr.v14 import LOAD_BASE

ENGINES = all(importlib.util.find_spec(name) for name in ("unicorn", "keystone"))
MAPPINGS = [(LOAD_BASE + 0x5A44, "Idioma"), (LOAD_BASE + 0x6150, "Idioma"),
            (LOAD_BASE + 0x5C00, "Brilho")]


class DispatchTableTests(unittest.TestCase):
    def test_aliases_share_our_translation_storage(self):
        content, selected = payload(MAPPINGS)
        self.assertEqual(selected[MAPPINGS[0][0]], selected[MAPPINGS[1][0]])
        self.assertEqual(struct.unpack_from("<II", content),
                         (MAPPINGS[0][0], selected[MAPPINGS[0][0]]))
        self.assertTrue(content.endswith(b"Idioma\0Brilho\0"))

    def test_rejects_duplicate_pointers_and_nonprintable_or_accented_data(self):
        for mappings in ([(0, "Idioma")], [(1, "A"), (1, "B")],
                         [(1, "Medição")], [(1, "A\0B")], [(1, "")]):
            with self.assertRaises(ValueError):
                payload(mappings)

    def test_table_limits_and_oversized_payload(self):
        with self.assertRaises(ValueError):
            payload([(i + 1, str(i)) for i in range(129)])
        with self.assertRaises(ValueError):
            payload([(1, "A" * 2048)])

    def test_private_profile_rejects_unknown_sample(self):
        with self.assertRaises(ValueError):
            private_mappings(b"synthetic, not original")


@unittest.skipUnless(ENGINES, "Install optional requirements-arm.txt for virtual ARM tests")
class VirtualArmTests(unittest.TestCase):
    def assert_contract(self, result):
        for key in ("reached_text", "registers_preserved_except_r2", "flags_preserved",
                    "sp_preserved_at_entry", "lr_preserved_at_entry", "stack_argument_bytes_preserved"):
            self.assertTrue(result[key], key)
        self.assertEqual(result["unexpected_writes"], [])
        self.assertEqual(result["unexpected_execution"], [])

    def test_chinese_english_and_invalid_locales_leave_pointer_unchanged(self):
        for locale in (0, 1, 3, 255):
            for pointer, _ in MAPPINGS:
                with self.subTest(locale=locale, pointer=pointer):
                    result = run(MAPPINGS, locale, pointer)
                    self.assert_contract(result)
                    self.assertEqual(result["selected_pointer"], pointer)
                    self.assertEqual(result["final_language"], locale)

    def test_portuguese_maps_each_alias_and_keeps_other_registers(self):
        _, expected = payload(MAPPINGS)
        for pointer, _ in MAPPINGS:
            result = run(MAPPINGS, 2, pointer)
            self.assert_contract(result)
            self.assertEqual(result["selected_pointer"], expected[pointer])

    def test_unknown_and_interior_pointers_are_not_rewritten(self):
        for pointer in (MAPPINGS[0][0] + 1, LOAD_BASE + 0xB290):
            result = run(MAPPINGS, 2, pointer)
            self.assert_contract(result)
            self.assertEqual(result["selected_pointer"], pointer)

    def test_all_nzcvq_combinations_survive_lookup(self):
        for state in range(32):
            for locale in (0, 1, 2):
                result = run(MAPPINGS, locale, MAPPINGS[0][0], flags=state << 27)
                self.assert_contract(result)

    def test_empty_lookup_is_bounded_and_falls_back(self):
        result = run([], 2, MAPPINGS[0][0])
        self.assert_contract(result)
        self.assertEqual(result["selected_pointer"], MAPPINGS[0][0])

    def test_no_original_execution_without_explicit_private_image(self):
        with self.assertRaises(ValueError):
            run(MAPPINGS, 2, MAPPINGS[0][0], stop_at_text=False)
        self.assertLess(len(assemble(3)), 128)


@unittest.skipUnless(ENGINES and os.environ.get("DMC100_V14_PATH"), "Private observed image not supplied")
class PrivateOriginalTextTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.path = Path(os.environ["DMC100_V14_PATH"])
        cls.data = cls.path.read_bytes()
        cls.mappings = private_mappings(cls.data)

    def assert_trace_equal(self, pointer, language, height=16, overlay=0):
        before = run(self.mappings, language, pointer, firmware=self.data, wrapper=False,
                     stop_at_text=False, height=height, overlay=overlay)
        after = run(self.mappings, language, pointer, firmware=self.data,
                    stop_at_text=False, height=height, overlay=overlay)
        self.assertTrue(before["returned"])
        self.assertTrue(after["returned"])
        self.assertEqual(before["trace_sha256"], after["trace_sha256"])
        self.assertEqual(before["trace_counts"], after["trace_counts"])
        self.assertEqual(after["unexpected_execution"], [])
        self.assertEqual(after["unexpected_writes"], [])
        self.assertEqual(after["final_sp"], STACK)
        self.assertTrue(after["original_rom_unchanged"])
        return after

    def test_primary_text_path_comparison_matrix(self):
        report = compare_private(self.data)
        self.assertEqual(report["abi_checks"], 56)
        self.assertEqual(report["original_text_trace_comparisons"], 42)
        self.assertFalse(report["firmware_generated"])
        self.assertEqual(self.path.read_bytes(), self.data)

    def test_real_chinese_string_passthrough_at_observed_font_size(self):
        # Three reference pointers from community annotations, no strings/bitmaps exported.
        for offset, height in ((0x5A64, 16), (0x5910, 16), (0xAE0C, 24)):
            result = self.assert_trace_equal(LOAD_BASE + offset, 0, height)
            self.assertGreater(result["trace_counts"]["windows"], 0)

    def test_four_original_ascii_font_sizes_and_both_draw_paths(self):
        for height in (12, 16, 24, 32):
            for overlay in (0, 1):
                result = self.assert_trace_equal(LOAD_BASE + 0x5A44, 1, height, overlay)
                self.assertGreater(result["trace_counts"]["data16"] + result["trace_counts"]["pixels"], 0)

    def test_protected_warning_and_power_messages_remain_original_even_for_ptbr(self):
        for offset, en, _ in STRINGS:
            if en in PROTECTED:
                result = self.assert_trace_equal(LOAD_BASE + offset, 2)
                self.assertEqual(result["selected_pointer"], LOAD_BASE + offset)
