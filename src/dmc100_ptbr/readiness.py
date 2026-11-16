"""Read-only integration assessment; never builds or patches firmware.

The known profile is fingerprint-bound. A numeric gap is not free flash.
This command cannot authorize installation or replace independent validation.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path, PurePosixPath
import re
import struct

from .v14 import LOAD_BASE, OBSERVED_SHA256

SETTINGS_RAM_LITERALS = (0x5A3C, 0x60C0, 0xADA4, 0x3EC8, 0x736C, 0x58FC, 0xB28C)


def resource_requirements(data: bytes) -> set[str]:
    """Known-path metadata only. Reject traversal rather than normalize it."""
    paths = set()
    for match in re.finditer(rb"2:/UI/([A-Za-z0-9_./-]{1,128}\.jpg)\x00", data):
        value = match.group(1).decode("ascii")
        pieces = value.split("/")
        if any(piece in ("", ".", "..") for piece in pieces):
            continue
        if pieces[0] not in {"decorat", "decorate", "mode", "mode_1", "cel", "cell"}:
            continue
        paths.add(value)
    return paths


def resource_inventory(required: set[str], directory: Path | None) -> dict:
    result = {"supplied": directory is not None, "required_unique_paths": len(required),
              "present": 0, "minimal_jpeg_signatures": 0, "bytes": 0,
              "missing": [], "unreadable": 0,
              "notice": "Local copies only. SOI/EOI signatures do not validate dimensions, content, rights or device decoder compatibility."}
    root = directory.resolve() if directory is not None else None
    for value in sorted(required):
        relative = PurePosixPath(value)
        if relative.is_absolute() or any(p in ("", ".", "..") for p in value.split("/")):
            raise ValueError("Unsafe resource requirement")
        if root is None:
            result["missing"].append(value)
            continue
        candidate = (root / Path(*relative.parts)).resolve()
        if not candidate.is_relative_to(root):
            result["missing"].append(value)
            continue
        try:
            if not candidate.is_file():
                result["missing"].append(value)
                continue
            size = candidate.stat().st_size
            with candidate.open("rb") as handle:
                first = handle.read(2)
                if size >= 4:
                    handle.seek(-2, 2)
                    last = handle.read(2)
                else:
                    last = b""
            result["present"] += 1
            result["bytes"] += size
            result["minimal_jpeg_signatures"] += first == b"\xff\xd8" and last == b"\xff\xd9"
        except OSError:
            result["unreadable"] += 1
    return result


def assess_bytes(data: bytes, ui_directory: Path | None = None) -> dict:
    fingerprint = hashlib.sha256(data).hexdigest()
    report = {"sha256": fingerprint, "bytes": len(data), "profile_applied": False,
              "installable_ready": False, "firmware_generated": False,
              "blockers": ["No validated PT-BR embedded implementation", "No verified image integrity/update contract",
                           "No confirmed target hardware revision", "No demonstrated recovery procedure",
                           "No independent interface/metrological validation"]}
    if fingerprint != OBSERVED_SHA256:
        report["blockers"].insert(0, "Not the observed V1.4 fingerprint")
        return report
    word = lambda offset: struct.unpack_from("<I", data, offset)[0]
    bases = [word(offset) for offset in SETTINGS_RAM_LITERALS]
    if len(set(bases)) != 1:
        raise ValueError("Inconsistent known settings literals")
    storage_base = word(0xD6BC)
    app_end = LOAD_BASE + len(data)
    required = resource_requirements(data)
    inventory = resource_inventory(required, ui_directory)
    if not inventory["supplied"] or inventory["present"] < len(required):
        report["blockers"].append("External UI resource copies missing or incomplete")
    report.update({"profile_applied": True,
                   "settings": {"ram_base_hex": f"0x{bases[0]:08X}",
                                "language_field_offset": 32,
                                "language_ram_hex": f"0x{bases[0] + 32:08X}",
                                "load_buffer_hex": f"0x{word(0xD5A0):08X}",
                                "save_buffer_hex": f"0x{word(0xD6B8):08X}",
                                "storage_base_hex": f"0x{storage_base:08X}"},
                   "image": {"base_hex": f"0x{LOAD_BASE:08X}",
                             "end_exclusive_hex": f"0x{app_end:08X}",
                             "gap_before_settings_bytes": storage_base - app_end,
                             "gap_is_proven_free": False},
                   "resources": inventory,
                   "notice": "Observed-image metadata and unresolved gates only. No patch, memory reservation, write, installer or hardware IO."})
    return report


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("path", type=Path)
    parser.add_argument("--ui-directory", type=Path, help="Existing private local copy of UI; never a device drive")
    args = parser.parse_args(argv)
    try:
        data = args.path.read_bytes()
        report = assess_bytes(data, args.ui_directory)
    except (OSError, ValueError) as exc:
        parser.error(str(exc))
    print(json.dumps(report, ensure_ascii=True, indent=2))
    return 0 if report["installable_ready"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
