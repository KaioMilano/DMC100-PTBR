import contextlib
import hashlib
import io
import json
from pathlib import Path
import struct
import tempfile
import unittest

from src.dmc100_ptbr.analyze import analyze_bytes, main as analyze_main, thumb_adr_candidates
from src.dmc100_ptbr.catalog import COMMUNITY_REPORTED_V14_SIZE, STRINGS
from src.dmc100_ptbr.inspect import inspect_bytes, main as inspect_main, occurrences
from src.dmc100_ptbr.layout import assess
from src.dmc100_ptbr.v14 import observed_profile, table_metadata


def fixture():
    data = bytearray(COMMUNITY_REPORTED_V14_SIZE)
    for offset, original, _ in STRINGS:
        data[offset:offset + len(original)] = original.encode("ascii")
    return data


class AnalysisTests(unittest.TestCase):
    def test_prefix_without_terminator_is_not_complete_match(self):
        data = fixture()
        offset, text, _ = STRINGS[0]
        data[offset + len(text)] = ord("X")
        report = inspect_bytes(bytes(data))
        self.assertEqual(report["matches"], len(STRINGS))
        self.assertEqual(report["nul_terminated_matches"], len(STRINGS) - 1)

    def test_eof_does_not_count_as_nul(self):
        offset, text, _ = STRINGS[0]
        data = bytes(offset) + text.encode("ascii")
        self.assertTrue(inspect_bytes(data)["strings"][0]["matches"])
        self.assertFalse(inspect_bytes(data)["strings"][0]["nul_terminated_match"])

    def test_duplicate_candidates_are_reported(self):
        data = fixture()
        data[10:19] = b"Language\0"
        self.assertEqual(inspect_bytes(bytes(data))["strings"][0]["occurrences"],
                         [10, STRINGS[0][0]])

    def test_overlapping_occurrences(self):
        self.assertEqual(occurrences(b"aaaa", b"aa"), [0, 1, 2])

    def test_structural_metadata_and_no_content_leak(self):
        data = struct.pack("<II", 0x20008000, 0x08000101)
        data += b"CONFIDENTIAL\0" + b"2:/UI/example.jpg\0\xff\xd8\xff\x00\xff\xd9"
        report = analyze_bytes(data)
        self.assertTrue(report["vectors_candidate"]["thumb_bit_set"])
        self.assertEqual(len(report["resource_path_candidate_offsets"]), 1)
        self.assertEqual(len(report["jpeg_soi_candidate_offsets"]), 1)
        self.assertNotIn("CONFIDENTIAL", json.dumps(report))
        self.assertNotIn("example.jpg", json.dumps(report))
        self.assertNotIn("found_hex", json.dumps(report))

    def test_empty_and_truncated_vectors(self):
        for data in (b"", b"\x00" * 7):
            self.assertIsNone(analyze_bytes(data)["vectors_candidate"])

    def test_partial_entropy_block(self):
        report = analyze_bytes(b"\xff" * 4097)
        self.assertEqual([b["bytes"] for b in report["blocks"]], [4096, 1])
        self.assertEqual(report["blocks"][0]["entropy_bits_per_byte"], 0)

    def test_utf16_ascii_candidates_at_odd_offset(self):
        self.assertEqual(analyze_bytes(b"!" + "ABCD".encode("utf-16le"))[
            "utf16le_ascii_candidate_runs"], 1)

    def test_cli_and_input_unchanged(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "synthetic.bin"
            data = bytes(fixture())
            path.write_bytes(data)
            before = hashlib.sha256(path.read_bytes()).hexdigest()
            with contextlib.redirect_stdout(io.StringIO()) as output:
                self.assertEqual(inspect_main([str(path), "--json"]), 0)
            self.assertEqual(json.loads(output.getvalue())["nul_terminated_matches"], len(STRINGS))
            with contextlib.redirect_stdout(io.StringIO()):
                self.assertEqual(analyze_main([str(path)]), 0)
            self.assertEqual(hashlib.sha256(path.read_bytes()).hexdigest(), before)
            self.assertEqual(list(Path(directory).iterdir()), [path])

    def test_wrong_size_cli_fails_even_with_all_strings(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "synthetic.bin"
            path.write_bytes(bytes(fixture()) + b"\x00")
            with contextlib.redirect_stdout(io.StringIO()):
                self.assertEqual(inspect_main([str(path), "--json"]), 1)

    def test_missing_path_cli_error(self):
        with tempfile.TemporaryDirectory() as directory:
            with contextlib.redirect_stderr(io.StringIO()), self.assertRaises(SystemExit) as exc:
                analyze_main([str(Path(directory) / "missing.bin")])
            self.assertEqual(exc.exception.code, 2)


class LayoutTests(unittest.TestCase):
    def test_boundary_and_overflow_are_distinct_from_byte_budget(self):
        self.assertTrue(assess("Sobre", "About", 40, 8)["fits_assumed_viewport"])
        result = assess("Sobre", "About", 39, 8)
        self.assertFalse(result["fits_assumed_viewport"])
        self.assertTrue(result["fits_original_payload_length"])

    def test_accent_encoding_and_normalization(self):
        result = assess("Medic\u0327a\u0303o", "Measurement")
        self.assertEqual(result["text"], "Medição")
        self.assertIsNone(result["encoded_bytes"])
        self.assertFalse(result["fits_original_payload_length"])
        self.assertEqual(assess("Medição", "Measurement", encoding="utf-8")["encoded_bytes"], 9)

    def test_invalid_geometry(self):
        for width, cell in ((0, 8), (220, -1)):
            with self.assertRaises(ValueError):
                assess("Sobre", "About", width, cell)


class ProfileAndReferenceTests(unittest.TestCase):
    def test_profile_does_not_apply_to_synthetic_firmware(self):
        self.assertFalse(observed_profile(bytes(fixture()))["applied"])

    def test_adr_t1_pc_alignment(self):
        # ADR r2, PC+12 at offset 2: Align(2+4,4)+12 = 16.
        data = b"\x00\x00\x03\xa2"
        self.assertEqual(thumb_adr_candidates(data, {16}), [
            {"instruction_candidate_offset": 2, "target_offset": 16, "register": 2}])
        self.assertEqual(thumb_adr_candidates(data, {18}), [])

    def test_adr_ignores_odd_and_incomplete_halfwords(self):
        self.assertEqual(thumb_adr_candidates(b"\x00\x03\xa2", {16}), [])

    def test_synthetic_pair_table_coverage_without_bitmap_export(self):
        data = struct.pack("<I", 0x08007004) + "é".encode("utf-8") + b"XY"
        result = table_metadata(data, 0, 1, 4, 0x08007000, True)
        self.assertTrue(result["in_bounds"])
        self.assertEqual(result["requested_accent_coverage"]["utf-8"], ["é"])
        self.assertNotIn("XY", json.dumps(result))

    def test_invalid_pointer_and_truncated_table(self):
        for pointer in (0x08006FFF, 0x08007004):
            data = struct.pack("<I", pointer)
            self.assertFalse(table_metadata(data, 0, 2, 4, 0x08007000, True)["in_bounds"])

    def test_truncated_literal(self):
        self.assertFalse(table_metadata(b"\0" * 3, 0, 1, 4, 0, False)["in_bounds"])

    def test_bad_descriptor_rejected(self):
        with self.assertRaises(ValueError):
            table_metadata(b"", 0, 1, 1, 0, True)


if __name__ == "__main__":
    unittest.main()
