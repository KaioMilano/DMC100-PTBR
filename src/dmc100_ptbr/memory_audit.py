"""Bounded literal inventory for placement research, never a free-space finder."""
import argparse
import hashlib
import json
from pathlib import Path
import struct
from .v14 import LOAD_BASE, OBSERVED_SHA256


def inventory(data, low, high):
    if not 0 <= low < high <= 0x100000000:
        raise ValueError("Invalid address interval")
    return [{"file_offset":offset,"value":value} for offset in range(0,len(data)-3,4)
            if low <= (value := struct.unpack_from("<I",data,offset)[0]) < high]


def audit(data):
    if hashlib.sha256(data).hexdigest() != OBSERVED_SHA256:
        raise ValueError("Requires observed V1.4 fingerprint")
    end = LOAD_BASE+len(data)
    ram = inventory(data,0x20000000,0x20008000)
    source,zero_start,zero_size,zero_function = struct.unpack_from('<4I',data,0x17640)
    return {"sha256":OBSERVED_SHA256,"app_start":LOAD_BASE,"app_end_exclusive":end,
            "bootloader_present":False,"physical_ram_revision_verified":False,
            "aligned_ram_literal_candidates":ram,
            "aligned_literals_into_gap":inventory(data,end,0x0801F400),
            "aligned_literals_into_settings_and_tail":inventory(data,0x0801F400,0x08020000),
            "emulator_state_address":0x20001000,
            "state_address_literal_occurrences":[r["file_offset"] for r in ram if r["value"] == 0x20001000],
            "state_ram_reservation_proven":False,"gap_free_space_proven":False,
            "reviewed_gap_candidate_classification":{
                "0x21FC":"Thumb SUB.W instruction, not a pointer",
                "0x6A28":"Thumb MOV.W instruction, not a pointer",
                "0x7A34":"Thumb MOV.W instruction, not a pointer",
                "0x9928":"Thumb ADD.W instruction, not a pointer",
                "0x17640":"Source field of zero-initialization descriptor; zero routine does not read it"},
            "reviewed_state_candidate_classification":"0x132E4 lies in paired 24px glyph table; not evidence of a RAM reference",
            "startup_zero_region":{"start":zero_start,"end_exclusive":zero_start+zero_size,
                                   "bytes":zero_size,"function":zero_function,
                                   "artificial_state_inside":zero_start<=0x20001000<zero_start+zero_size},
            "firmware_generated":False,"installable_ready":False,
            "limits":"Aligned words may be data, instructions or pointers. Absence does not exclude computed addresses, heap, stack, DMA or indirect references. No placement is approved."}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("firmware",type=Path)
    args = parser.parse_args()
    data = args.firmware.read_bytes()
    result = audit(data)
    if args.firmware.read_bytes() != data:
        raise RuntimeError("Input changed")
    print(json.dumps(result,indent=2))


if __name__ == "__main__":
    main()
