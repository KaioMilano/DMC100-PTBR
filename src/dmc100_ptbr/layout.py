"""Parametric text layout study, not an emulator of the original firmware.

No firmware input or output. Cell width and viewport are explicit assumptions.
"""
from __future__ import annotations

import argparse
import json
import unicodedata

from .catalog import STRINGS


def assess(text: str, original: str, width: int = 220, cell: int = 8,
           encoding: str = "ascii") -> dict:
    if width <= 0 or cell <= 0:
        raise ValueError("width and cell must be positive")
    text = unicodedata.normalize("NFC", text)
    try:
        encoded_size = len(text.encode(encoding))
    except UnicodeEncodeError:
        encoded_size = None
    return {"text": text, "encoding": encoding, "encoded_bytes": encoded_size,
            "original_ascii_bytes": len(original.encode("ascii")),
            "fits_original_payload_length": encoded_size is not None and
            encoded_size <= len(original.encode("ascii")),
            "assumed_width_px": len(text) * cell,
            "fits_assumed_viewport": len(text) * cell <= width,
            "non_ascii_codepoints": sorted({f"U+{ord(c):04X}" for c in text if ord(c) > 127}),
            "notice": "Length budget only; allocation, glyph coverage and actual advance unknown."}


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--width", type=int, default=220)
    parser.add_argument("--cell", type=int, default=8)
    args = parser.parse_args(argv)
    if args.width <= 0 or args.cell <= 0:
        parser.error("width and cell must be positive")
    print(json.dumps({"model": "Assumed monospace; does not reproduce device fonts.",
                      "width": args.width, "cell": args.cell,
                      "labels": [assess(pt, en, args.width, args.cell)
                                 for _, en, pt in STRINGS]}, ensure_ascii=True, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
