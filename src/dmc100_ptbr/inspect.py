"""Read-only FNIRSI DMC-100 firmware analysis.

Never writes bytes or communicates with hardware.
Community offsets are UNVERIFIED; string matches do not prove safety,
authenticity or compatibility with a particular device revision.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

from .catalog import COMMUNITY_REPORTED_V14_SIZE, STRINGS


def inspect_bytes(data: bytes, file_name: str = "<memory>") -> dict:
    """Return a JSON-serializable static report, leaving input unchanged."""
    strings = []
    for offset, original, proposed in STRINGS:
        expected = original.encode("ascii")
        actual = data[offset : offset + len(expected)] if offset < len(data) else b""
        strings.append({
            "offset_hex": f"0x{offset:06X}",
            "original": original,
            "ptbr_draft": proposed,
            "matches": actual == expected,
            "nul_terminated_match": data[offset:offset + len(expected) + 1] == expected + b"\x00",
            "occurrences": occurrences(data, expected + b"\x00"),
            "original_bytes": len(expected),
            "draft_ascii_bytes": len(proposed.encode("ascii")),
        })
    return {
        "file": file_name,
        "bytes": len(data),
        "sha256": hashlib.sha256(data).hexdigest(),
        "community_reported_v14_size": COMMUNITY_REPORTED_V14_SIZE,
        "reported_size_matches": len(data) == COMMUNITY_REPORTED_V14_SIZE,
        "matches": sum(item["matches"] for item in strings),
        "nul_terminated_matches": sum(item["nul_terminated_match"] for item in strings),
        "total_strings": len(strings),
        "strings": strings,
        "notice": "Read-only research, not firmware compatibility/safety validation.",
    }


def occurrences(data: bytes, needle: bytes) -> list[int]:
    """Find every byte occurrence, including unaligned/overlapping matches.

    These are candidate text starts, not confirmed string objects or xrefs.
    """
    result = []
    start = 0
    while (position := data.find(needle, start)) >= 0:
        result.append(position)
        start = position + 1
    return result


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("path", type=Path, help="Local firmware file (read-only)")
    parser.add_argument("--json", action="store_true", help="Print JSON report")
    args = parser.parse_args(argv)
    try:
        firmware = args.path.read_bytes()
    except OSError as exc:
        parser.error(f"Unable to read file: {exc}")

    report = inspect_bytes(firmware, args.path.name)
    if args.json:
        print(json.dumps(report, ensure_ascii=False, indent=2))
    else:
        print(f"Arquivo: {report['file']}")
        print(f"Tamanho: {report['bytes']:,} bytes")
        print(f"SHA-256: {report['sha256']}")
        print(f"Tamanho esperado pela comunidade: {report['reported_size_matches']}")
        print(f"Strings coincidentes: {report['matches']}/{report['total_strings']}")
        for item in report["strings"]:
            result = "OK" if item["matches"] else "DIVERGENTE"
            print(f"{result:10s} {item['offset_hex']} {item['original']}")
        print("IMPORTANTE: isso nao valida seguranca nem compatibilidade de gravacao.")
    return 0 if (report["reported_size_matches"] and
                 report["nul_terminated_matches"] == report["total_strings"]) else 1


if __name__ == "__main__":
    raise SystemExit(main())
