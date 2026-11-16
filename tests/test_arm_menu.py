import importlib.util
import contextlib
import io
import json
import unittest

from src.dmc100_ptbr.arm_menu import main, step
from src.dmc100_ptbr.arm_dispatch import payload, run
from src.dmc100_ptbr.v14 import LOAD_BASE

ENGINES = all(importlib.util.find_spec(n) for n in ("unicorn", "keystone"))


class MenuInputTests(unittest.TestCase):
    def test_rejects_invalid_state_before_execution(self):
        for state, event in [((3, 0, 0), "ok"), ((0, 3, 0), "ok"),
                             ((0, 0, 2), "ok"), ((0, 0, 0), "flash"),
                             ((True, 0, 0), "ok")]:
            with self.assertRaises(ValueError):
                step(state, event)


@unittest.skipUnless(ENGINES, "Optional virtual ARM engines not installed")
class ArmMenuTests(unittest.TestCase):
    def test_default_cli_runs_confirmation_sequence(self):
        output = io.StringIO()
        with contextlib.redirect_stdout(output):
            self.assertEqual(main([]), 0)
        report = json.loads(output.getvalue())
        self.assertEqual(report["trace"][-1]["active"], "Português (BR)")
        self.assertFalse(report["firmware_generated"])

    def test_complete_transition_matrix(self):
        for active in range(3):
            for cursor in range(3):
                for pending in (0, 1):
                    expected = {"up": (active, (cursor-1) % 3, 0),
                                "down": (active, (cursor+1) % 3, 0),
                                "back": (active, active, 0),
                                "ok": (cursor, cursor, 0) if pending else (active, cursor, 1)}
                    for event, target in expected.items():
                        with self.subTest(state=(active, cursor, pending), event=event):
                            result = step((active, cursor, pending), event)
                            self.assertEqual(result["state"], target)
                            self.assertTrue(result["returned"])
                            self.assertTrue(result["preserved_registers"])

    def test_confirmation_selects_ptbr_dispatch_and_cancel_keeps_english(self):
        pointer = LOAD_BASE + 0x5A44
        mappings = [(pointer, "Idioma")]
        _, translated = payload(mappings)
        selected = step((1, 1, 0), "down")["state"]
        pending = step(selected, "ok")["state"]
        self.assertEqual(run(mappings, pending[0], pointer)["selected_pointer"], pointer)
        cancelled = step(pending, "back")["state"]
        self.assertEqual(cancelled, (1, 1, 0))
        confirmed = step(pending, "ok")["state"]
        self.assertEqual(confirmed, (2, 2, 0))
        self.assertEqual(run(mappings, confirmed[0], pointer)["selected_pointer"], translated[pointer])

    def test_can_return_from_portuguese_to_both_original_languages(self):
        for direction, target in (("up", 1), ("down", 0)):
            state = (2, 2, 0)
            for event in (direction, "ok", "ok"):
                state = step(state, event)["state"]
            self.assertEqual(state, (target, target, 0))
