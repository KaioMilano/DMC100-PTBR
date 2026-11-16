import importlib.util
import os
from pathlib import Path
import struct
import unittest

from src.dmc100_ptbr.arm_text_gate import owned_table,entry_branch,absolute_jump
from src.dmc100_ptbr.arm_ui import VirtualLanguageUI,PT,TITLE,OWN_TEXTS,RETURN
from src.dmc100_ptbr.arm_dispatch import STACK
from src.dmc100_ptbr.accent_font import bitmap
from src.dmc100_ptbr.v14 import LOAD_BASE

ENGINES = all(importlib.util.find_spec(n) for n in ("unicorn","keystone"))


class GateTableTests(unittest.TestCase):
    def test_utf8_byte_lengths_include_nul(self):
        data = owned_table(OWN_TEXTS)
        rows = [struct.unpack_from("<II",data,i*8) for i in range(len(OWN_TEXTS))]
        self.assertEqual(dict(rows),{p:len(t.encode())+1 for p,t in OWN_TEXTS.items()})

    def test_invalid_slot_and_unreachable_veneer_rejected(self):
        for texts in ({0:"A"},{PT:"A"*32},{PT:"A\0B"},{PT:""}):
            with self.assertRaises(ValueError):
                owned_table(texts)
        with self.assertRaises(ValueError):
            entry_branch(0x080082F2,0x1000A000)
        with self.assertRaises(ValueError):
            absolute_jump(0x08100002,0x1000A000)


@unittest.skipUnless(ENGINES,"Optional ARM engines")
class ShadowArmGateTests(unittest.TestCase):
    def raw(self,ui,pointer,flags=0xA8000000,height=16,overlay=1):
        return ui._run(LOAD_BASE+0x12F2,"text",text_args=(10,20,pointer,0xF79E,0x0841,height,overlay),flags=flags)

    def test_native_and_owned_routes_preserve_all_nzcvq_entry_contracts(self):
        ui = VirtualLanguageUI(language=2,shadow_entries=True)
        for state in range(32):
            for pointer,route,target in ((LOAD_BASE+0x5A5C,"native",LOAD_BASE+0x5A5C),
                                         (PT,"owned",PT),(LOAD_BASE+0x5A44,"owned",TITLE)):
                self.raw(ui,pointer,flags=state<<27)
                entry = ui.gate_contracts[0]
                self.assertEqual(entry["route"],route)
                expected = [10,20,target,0xF79E]+[0x11110000+i for i in range(4,13)]
                if route == "owned":
                    expected[12] = len(OWN_TEXTS[target].encode())+1
                self.assertEqual(entry["registers"],expected)
                self.assertEqual(entry["flags"],state<<27)
                self.assertEqual((entry["sp"],entry["lr"]),(STACK,RETURN|1))
                self.assertEqual(entry["stack_args"],[0x0841,16,1])

    def test_unsupported_native_format_falls_back_and_owned_buffer_does_not_reach_gbk(self):
        ui = VirtualLanguageUI(language=2,shadow_entries=True)
        for height,overlay in ((18,1),(16,0)):
            self.raw(ui,LOAD_BASE+0x5A44,height=height,overlay=overlay)
            self.assertEqual(ui.gate_contracts[0]["route"],"native")
            self.assertEqual(ui.gate_contracts[0]["registers"][2],LOAD_BASE+0x5A44)
            result = self.raw(ui,PT,height=height,overlay=overlay)
            self.assertEqual(ui.gate_contracts,[])
            self.assertEqual(result["trace"],[])

    def test_unknown_interior_pointer_is_not_treated_as_owned(self):
        ui = VirtualLanguageUI(shadow_entries=True)
        self.raw(ui,PT+1)
        self.assertEqual(ui.gate_contracts[0]["route"],"native")

    def test_entry_branches_and_height_changes_execute_without_host_text_routing(self):
        ui = VirtualLanguageUI(shadow_entries=True)
        for height in (12,16,24,32,16):
            result = ui.render(authorial_height=height)
            self.assertTrue(result["text_routing_by_arm"])
            self.assertEqual(set(result["shadow_entry_ranges"]),{0x12F2,0x5938})
            width,rows = bitmap("ê",height)
            expected = {(106+OWN_TEXTS[PT].index("ê")*width+x,273+y)
                        for y,row in enumerate(rows) for x in range(width)
                        if row & (1 << (width-1-x)) and 106+OWN_TEXTS[PT].index("ê")*width+x < 240}
            actual = {(t["args"][0],t["args"][1]) for t in result["trace"] if t["call"] == "accent_pixel"}
            self.assertEqual(actual,expected)

    def test_confirmation_cancel_and_original_locale_fallback(self):
        ui = VirtualLanguageUI(shadow_entries=True)
        for event in ("down","ok","back"):
            ui.event(event)
        self.assertEqual(ui.render()["state"],(1,1,0))
        for event in ("down","ok","ok"):
            ui.event(event)
        self.assertEqual(ui.render()["state"],(2,2,0))
        for locale in (0,1):
            original = VirtualLanguageUI(language=locale,shadow_entries=True)
            self.raw(original,LOAD_BASE+0x5A44)
            self.assertEqual(original.gate_contracts[0]["route"],"native")


@unittest.skipUnless(ENGINES and os.environ.get("DMC100_V14_PATH"),"Private shadow entry opt-in")
class PrivateShadowEntryTests(unittest.TestCase):
    def test_original_settings_action_three_is_brightness_not_third_language(self):
        source = Path(os.environ["DMC100_V14_PATH"]).read_bytes()
        for action,target in ((1,0),(2,1),(3,1)):
            ui = VirtualLanguageUI(source)
            before = bytes(ui.cpu.mem_read(0x20000000,0x6000))
            result = ui.probe_original_language_action(action)
            after = bytes(ui.cpu.mem_read(0x20000000,0x6000))
            self.assertEqual(result["language_ram"],target)
            calls = [t["call"] for t in result["trace"]]
            self.assertEqual(calls.count("brightness_preview"),int(action == 3))
            self.assertEqual(calls.count("jpeg_resource"),int(action in (1,2)))
            self.assertLessEqual({i for i,(a,b) in enumerate(zip(before,after)) if a != b},{0x1D8})

    def test_shadow_branch_execution_matches_hook_baseline_glyph_traces(self):
        path = Path(os.environ["DMC100_V14_PATH"])
        source = path.read_bytes()
        for locale in range(3):
            baseline = VirtualLanguageUI(source,locale,execute_glyphs=True).render()
            ui = VirtualLanguageUI(source,locale,execute_glyphs=True,shadow_entries=True)
            shadow = ui.render()
            self.assertEqual(baseline["original_glyph_trace_sha256"],shadow["original_glyph_trace_sha256"])
            self.assertEqual(baseline["original_glyph_boundary_calls"],shadow["original_glyph_boundary_calls"])
            modified = bytes(ui.cpu.mem_read(LOAD_BASE,len(source)))
            changed = {i for i,(a,b) in enumerate(zip(source,modified)) if a != b}
            self.assertTrue(changed)
            self.assertLessEqual(changed,set(range(0x12F2,0x12F6))|set(range(0x5938,0x593C)))
        self.assertEqual(path.read_bytes(),source)
