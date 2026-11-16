import importlib.util
import os
from pathlib import Path
import unittest
from unittest.mock import patch

from src.dmc100_ptbr.arm_ui import VirtualLanguageUI, PT, TITLE, CONFIRM, OWN_TEXTS
from src.dmc100_ptbr.accent_font import bitmap
from src.dmc100_ptbr.v14 import ACCENTS

ENGINES = all(importlib.util.find_spec(n) for n in ("unicorn", "keystone"))


class IntegratedProfileTests(unittest.TestCase):
    def test_unknown_private_firmware_and_invalid_locale_rejected(self):
        with self.assertRaises(ValueError):
            VirtualLanguageUI(b"not original")
        with self.assertRaises(ValueError):
            VirtualLanguageUI(language=3)


@unittest.skipUnless(ENGINES, "Optional ARM engines")
class IntegratedArmTests(unittest.TestCase):
    def test_authorial_accent_pixels_are_clipped_to_240_by_320(self):
        with patch.dict(OWN_TEXTS,{PT:"A"*20+"á"}):
            result = VirtualLanguageUI().render()
            self.assertFalse(any(t["call"] == "accent_pixel" for t in result["trace"]))

    def test_report_keeps_release_gates_false_and_counts_logical_components(self):
        from src.dmc100_ptbr.integration_report import report
        result = report()
        self.assertEqual(result["frames"][-1]["state"],(2,2,0))
        self.assertEqual(result["logical_bytes_compact_runtime"],sum(result["components_logical_bytes"].values()))
        self.assertGreater(result["font_storage_comparison"]["all_tables_bytes"],result["original_sample_gap_before_settings"])
        self.assertTrue(result["all_four_sizes_supported_by_runtime"])
        self.assertLessEqual(result["label_right_edge_by_height"][16],240)
        self.assertGreater(result["label_right_edge_by_height"][32],240)
        for key in ("gap_is_proven_free","physical_placement_validated","flash_persistence_implemented",
                    "update_integrity_verified","recovery_demonstrated","firmware_generated","installable_ready"):
            self.assertFalse(result[key],key)

    def test_all_authorial_accents_produce_exact_pixels_in_same_cpu(self):
        for character in ACCENTS:
            for height in (12,16,24,32):
                with self.subTest(character=character,height=height), patch.dict(OWN_TEXTS, {PT:character}):
                    ui = VirtualLanguageUI()
                    result = ui.render(authorial_height=height)
                    actual = {(t["args"][0], t["args"][1]) for t in result["trace"] if t["call"] == "accent_pixel"}
                    width, rows = bitmap(character,height)
                    expected = {(106+x,273+y) for y,row in enumerate(rows) for x in range(width)
                                if row & (1 << (width-1-x))}
                    self.assertEqual(actual,expected)
                    self.assertEqual(sum(t["call"] == "accent_pixel" for t in result["trace"]),len(expected))

    def test_portuguese_label_advances_by_glyph_not_utf8_bytes(self):
        result = VirtualLanguageUI().render()
        pixels = [t for t in result["trace"] if t["call"] == "accent_pixel"]
        start = 106 + OWN_TEXTS[PT].index("ê")*8
        self.assertTrue(pixels)
        self.assertTrue(all(start <= t["args"][0] < start+8 for t in pixels))
        self.assertTrue(any(t["call"] == "ascii_fragment" and t["args"][:2] == [start+8,273] for t in result["trace"]))

    def test_three_rows_and_font_arguments(self):
        ui = VirtualLanguageUI()
        result = ui.render()
        rows = [t for t in result["trace"] if t["call"] == "text"]
        self.assertFalse(result["original_menu_executed"])
        self.assertEqual([(t["args"][0], t["args"][1]) for t in rows], [(106,201),(106,237),(106,273)])
        self.assertEqual(rows[-1]["args"][2], PT)
        self.assertTrue(all(t["stack_args"][1:] == [16,1] for t in rows))

    def test_arm_to_arm_confirmation_cancel_and_return(self):
        ui = VirtualLanguageUI()
        for event in ("down", "ok"):
            ui.event(event)
        self.assertEqual(ui.state, (1,2,1))
        self.assertTrue(any(t["args"][2] == CONFIRM for t in ui.render()["trace"] if t["call"] == "text"))
        ui.event("back")
        self.assertEqual(ui.state, (1,1,0))
        for event in ("down", "ok", "ok"):
            ui.event(event)
        self.assertEqual(ui.state, (2,2,0))
        for event in ("up", "ok", "ok"):
            ui.event(event)
        self.assertEqual(ui.state, (1,1,0))

    def test_draw_never_changes_selection_or_other_ram(self):
        ui = VirtualLanguageUI(language=2)
        before = bytes(ui.cpu.mem_read(0x20000000, 0x6000))
        ui.render()
        self.assertEqual(bytes(ui.cpu.mem_read(0x20000000, 0x6000)), before)

    def test_invalid_event_does_not_change_state(self):
        ui = VirtualLanguageUI()
        with self.assertRaises(ValueError):
            ui.event("flash")
        self.assertEqual(ui.state, (1,1,0))


@unittest.skipUnless(ENGINES and os.environ.get("DMC100_V14_PATH"), "Private integrated UI opt-in")
class PrivateIntegratedArmTests(unittest.TestCase):
    def test_original_glyph_engine_and_authorial_accents_coexecute(self):
        data = Path(os.environ["DMC100_V14_PATH"]).read_bytes()
        for locale in range(3):
            ui = VirtualLanguageUI(data,locale,execute_glyphs=True)
            first, second = ui.render(), ui.render()
            self.assertGreater(first["original_glyph_boundary_calls"],0)
            self.assertEqual(first["original_glyph_trace_sha256"],second["original_glyph_trace_sha256"])
            self.assertEqual(sum(t["call"] == "accent_pixel" for t in first["trace"]),40)
            self.assertEqual(first["state"],(locale,locale,0))

    def test_original_menu_and_authorial_third_row_share_cpu(self):
        path = Path(os.environ["DMC100_V14_PATH"])
        original = path.read_bytes()
        for language in range(3):
            ui = VirtualLanguageUI(original, language)
            result = ui.render()
            texts = [t for t in result["trace"] if t["call"] == "text"]
            self.assertTrue(result["original_menu_executed"])
            self.assertEqual(len(texts), 6)
            self.assertEqual(texts[-1]["args"][2], PT)
            if language == 2:
                self.assertEqual(texts[0]["args"][2], TITLE)
        self.assertEqual(path.read_bytes(), original)

    def test_confirmed_language_is_read_by_original_menu_without_host_state_copy(self):
        ui = VirtualLanguageUI(Path(os.environ["DMC100_V14_PATH"]).read_bytes())
        for event in ("down", "ok", "ok"):
            ui.event(event)
        result = ui.render()
        self.assertEqual(result["state"], (2,2,0))
        self.assertEqual(next(t for t in result["trace"] if t["call"] == "text")["args"][2], TITLE)
