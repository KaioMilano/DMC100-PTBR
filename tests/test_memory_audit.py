import struct
import unittest
from src.dmc100_ptbr.memory_audit import inventory,audit


class MemoryInventoryTests(unittest.TestCase):
    def test_half_open_bounds_duplicates_and_truncated_word(self):
        data = struct.pack('<5I',99,100,100,199,200)+b'\x64\0\0'
        self.assertEqual(inventory(data,100,200),[
            {'file_offset':4,'value':100},{'file_offset':8,'value':100},{'file_offset':12,'value':199}])

    def test_invalid_interval_and_unknown_firmware_rejected(self):
        for low,high in ((-1,2),(2,2),(3,2),(0,0x100000001)):
            with self.assertRaises(ValueError):
                inventory(b'',low,high)
        with self.assertRaises(ValueError):
            audit(b'unknown')
