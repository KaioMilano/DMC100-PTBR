import struct
import unicodedata
import unittest

from src.dmc100_ptbr.accent_font import bitmap, packed_table, compact_table, source_rows, budget, preview_svg
from src.dmc100_ptbr.v14 import ACCENTS


class AuthorialAccentTests(unittest.TestCase):
    def test_compact_table_has_all_keys_and_source_rows(self):
        data = compact_table()
        self.assertEqual(len(data),286)
        for i,character in enumerate(ACCENTS):
            self.assertEqual(struct.unpack_from("<H",data,i*11)[0],ord(character))
            self.assertEqual(tuple(data[i*11+2:(i+1)*11]),source_rows(character))

    def test_all_accents_have_bounded_nonempty_bitmap_in_every_size(self):
        for height in (12,16,24,32):
            for character in ACCENTS:
                width, rows = bitmap(character, height)
                self.assertEqual((width, len(rows)), (height//2, height))
                self.assertTrue(any(rows))
                self.assertTrue(all(0 <= row < 1 << width for row in rows))
                self.assertTrue(all(row & 1 == 0 for row in rows))

    def test_utf8_normalization_yields_same_glyph(self):
        for character in ACCENTS:
            self.assertEqual(bitmap(character, 16), bitmap(unicodedata.normalize("NFD", character), 16))

    def test_marks_are_distinct_and_accented_i_has_no_duplicate_dot(self):
        self.assertEqual(len({bitmap(c,16) for c in "áàâã"}), 4)
        _, rows = bitmap("í", 16)
        # Row 4 samples the blank former-dot row after two accent rows.
        self.assertEqual(rows[4], 0)

    def test_packed_keys_rows_and_padding_round_trip(self):
        for height in (12,16,24,32):
            data = packed_table(height)
            stride = ((height//2)+7)//8
            record = 2 + stride*height
            for i, character in enumerate(ACCENTS):
                offset = i*record
                self.assertEqual(struct.unpack_from("<H", data, offset)[0], ord(character))
                width, rows = bitmap(character, height)
                for y, row in enumerate(rows):
                    value = int.from_bytes(data[offset+2+y*stride:offset+2+(y+1)*stride], "big")
                    self.assertEqual(value, row << (stride*8-width))

    def test_unsupported_input_and_sizes_are_rejected(self):
        for character, height in (("a",16),("🙂",16),("áá",16),("á",15),("",16)):
            with self.assertRaises(ValueError):
                bitmap(character,height)

    def test_budget_is_storage_only_and_preview_contains_no_external_images(self):
        report = budget()
        self.assertEqual(report["glyphs"], 26)
        self.assertEqual(report["all_tables_bytes"], 3848)
        self.assertFalse(report["runtime_decoder_included"])
        self.assertNotIn("<image", preview_svg())
