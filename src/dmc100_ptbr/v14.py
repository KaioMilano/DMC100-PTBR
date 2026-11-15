"""Metadata profile of the privately inspected V1.4 download.

Offsets describe this exact SHA-256 only. No font bitmap or firmware is shipped.
The fingerprint identifies the observed file, not manufacturer authenticity.
"""
import hashlib
import struct

OBSERVED_SHA256 = "f8eab197553e117a374dc9926989b8ec2105baa8120682bd5c864bda30e8364d"
LOAD_BASE = 0x08007000
# (height, literal-pool file offset, records, record bytes)
ASCII_TABLES = ((12, 0x14FC, 95, 12), (16, 0x1500, 95, 16),
                (24, 0x1504, 95, 48), (32, 0x14F8, 95, 64))
PAIR_TABLES = ((12, 0x16D4, 17, 26), (16, 0x17C8, 73, 34),
               (24, 0x18C0, 38, 74), (32, 0x1A78, 25, 130))
ACCENTS = "áàâãéêíóôõúüçÁÀÂÃÉÊÍÓÔÕÚÜÇ"


def table_metadata(data: bytes, literal: int, count: int, stride: int,
                   base: int, paired: bool) -> dict:
    """Read a bounded table descriptor; disclose no bitmap or raw keys."""
    if literal < 0 or count <= 0 or stride < (2 if paired else 1):
        raise ValueError("Invalid table descriptor")
    if literal + 4 > len(data):
        return {"in_bounds": False}
    address = struct.unpack_from("<I", data, literal)[0]
    offset = address - base
    end = offset + count * stride
    result = {"literal_offset": literal, "address_hex": f"0x{address:08X}",
              "offset": offset, "end_exclusive": end,
              "records": count, "record_bytes": stride,
              "in_bounds": 0 <= offset <= end <= len(data)}
    if not result["in_bounds"] or not paired:
        return result
    keys = {data[offset + i * stride:offset + i * stride + 2] for i in range(count)}
    result["unique_keys"] = len(keys)
    result["decodable_keys"] = {}
    result["requested_accent_coverage"] = {}
    for encoding in ("gb2312", "gbk", "utf-8"):
        valid = 0
        for key in keys:
            try:
                key.decode(encoding)
                valid += 1
            except UnicodeDecodeError:
                pass
        supported = []
        for character in ACCENTS:
            try:
                encoded = character.encode(encoding)
            except UnicodeEncodeError:
                continue
            if len(encoded) == 2 and encoded in keys:
                supported.append(character)
        result["decodable_keys"][encoding] = valid
        result["requested_accent_coverage"][encoding] = supported
    return result


def observed_profile(data: bytes) -> dict:
    if hashlib.sha256(data).hexdigest() != OBSERVED_SHA256:
        return {"applied": False, "reason": "Not the observed V1.4 fingerprint."}
    tables = []
    for paired, descriptors in ((False, ASCII_TABLES), (True, PAIR_TABLES)):
        for height, literal, count, stride in descriptors:
            entry = table_metadata(data, literal, count, stride, LOAD_BASE, paired)
            entry.update({"height": height, "kind": "paired" if paired else "ascii"})
            tables.append(entry)
    reset = struct.unpack_from("<I", data, 4)[0]
    return {"applied": True, "load_base_hex": f"0x{LOAD_BASE:08X}",
            "reset_file_offset": (reset & ~1) - LOAD_BASE,
            "tables": tables,
            "notice": "Observed image only. Base corroborated by entry point, literal tables and public platform map; no authenticity or hardware compatibility verdict."}
