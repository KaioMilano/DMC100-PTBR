"""Offline structural triage. Outputs metadata only; never extracts assets.

Heuristics do not identify a processor, filesystem, font, or available memory.
"""
from __future__ import annotations

import argparse
import json
import math
import re
import struct
from collections import Counter
from pathlib import Path

from .inspect import inspect_bytes, occurrences


def analyze_bytes(data: bytes) -> dict:
    report = inspect_bytes(data)
    vectors = None
    if len(data) >= 8:
        sp, reset = struct.unpack_from("<II", data)
        vectors = {"initial_sp_hex": f"0x{sp:08X}",
                   "reset_hex": f"0x{reset:08X}",
                   "thumb_bit_set": bool(reset & 1),
                   "notice": "Raw first words only; base and vector location unverified."}
    ascii_runs = list(re.finditer(rb"[\x20-\x7e]{4,}", data))
    utf16_runs = list(re.finditer(rb"(?:[\x20-\x7e]\x00){4,}", data))
    blocks = []
    for offset in range(0, len(data), 4096):
        block = data[offset:offset + 4096]
        counts = Counter(block)
        entropy = -sum((n / len(block)) * math.log2(n / len(block))
                       for n in counts.values())
        blocks.append({"offset": offset, "bytes": len(block),
                       "entropy_bits_per_byte": round(entropy, 4),
                       "zero_bytes": counts[0], "ff_bytes": counts[255]})
    report.update({
        "schema_version": 1, "vectors_candidate": vectors,
        "ascii_candidate_runs": len(ascii_runs),
        "utf16le_ascii_candidate_runs": len(utf16_runs),
        "resource_path_candidate_offsets": [
            m.start() for m in re.finditer(rb"[12]:/?UI/[^\x00\r\n]{1,128}?\.jpg", data)],
        "jpeg_soi_candidate_offsets": occurrences(data, b"\xff\xd8\xff"),
        "jpeg_eoi_candidate_offsets": occurrences(data, b"\xff\xd9"),
        "blocks": blocks,
        "limits": "Candidates only. JPEG markers may be false positives. Zero/FF runs are not free space. No assets, arbitrary strings or firmware bytes emitted.",
    })
    return report


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("path", type=Path)
    args = parser.parse_args(argv)
    try:
        data = args.path.read_bytes()
    except OSError as exc:
        parser.error(f"Unable to read file: {exc}")
    report = analyze_bytes(data)
    # Do not publish even the local filename: it could carry personal data.
    print(json.dumps(report, ensure_ascii=True, indent=2))
    return 0  # successful analysis, never a compatibility verdict


if __name__ == "__main__":
    raise SystemExit(main())
