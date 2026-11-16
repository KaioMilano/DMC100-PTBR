import importlib.util
import unittest
from src.dmc100_ptbr.arm_utf8 import decode
from src.dmc100_ptbr.v14 import ACCENTS

ENGINES = all(importlib.util.find_spec(n) for n in ("unicorn","keystone"))


class DecoderBoundsTests(unittest.TestCase):
    def test_invalid_declared_length(self):
        for data,length in ((b"a",2),(b"a",-1),(b"a"*4097,1)):
            with self.assertRaises(ValueError):
                decode(data,length)


@unittest.skipUnless(ENGINES,"Optional ARM engines")
class ArmUTF8Tests(unittest.TestCase):
    def test_all_printable_ascii_and_all_accent_keys(self):
        for codepoint in range(32,127):
            result = decode(bytes([codepoint]))
            self.assertEqual((result["codepoint"],result["consumed"],result["glyph_index"]),(codepoint,1,-1))
        for index,character in enumerate(ACCENTS):
            result = decode(character.encode("utf-8"))
            self.assertEqual((result["codepoint"],result["consumed"],result["glyph_index"]),(ord(character),2,index))

    def test_truncated_invalid_overlong_and_unsupported_sequences_progress(self):
        for data in (b"\xc3",b"\xc3\0",b"\xc0\xaf",b"\xed\xa0\x80",b"\xc3\xbf",b"\xff",b"\n",b"\xf0\x9f\x99\x82"):
            result = decode(data)
            self.assertEqual((result["codepoint"],result["consumed"],result["glyph_index"]),(0xfffd,1,-2))

    def test_nul_empty_and_explicit_short_buffer_never_read_past_bound(self):
        for data,length in ((b"",0),(b"abc",0),(b"\0",1)):
            result = decode(data,length)
            self.assertEqual((result["codepoint"],result["consumed"]),(0,0))
        self.assertEqual(decode("á".encode(),1)["glyph_index"],-2)

    def test_mixed_text_can_be_consumed_without_counting_utf8_bytes_as_glyphs(self):
        text = "Medição".encode("utf-8")
        codepoints = []
        while text:
            result = decode(text)
            self.assertGreater(result["consumed"],0)
            codepoints.append(result["codepoint"])
            text = text[result["consumed"]:]
        self.assertEqual("".join(map(chr,codepoints)),"Medição")
