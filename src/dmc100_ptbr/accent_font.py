"""Hand-drawn authorial accent study; no system or firmware font is copied.

Packed format is our proposal: uint16 Unicode key + row-major MSB-first cells.
It is not compatible with the original paired/GBK tables or a ready font patch.
"""
import math
import struct
import unicodedata

from .v14 import ACCENTS

# Five-column, seven-row base designs, drawn specifically for this experiment.
BASES = {
    "a": (0, 0, 14, 1, 15, 17, 15),
    "e": (0, 0, 14, 17, 31, 16, 14),
    "i": (4, 0, 12, 4, 4, 4, 14),
    "o": (0, 0, 14, 17, 17, 17, 14),
    "u": (0, 0, 17, 17, 17, 19, 13),
    "c": (0, 0, 14, 16, 16, 16, 14),
    "A": (14, 17, 17, 31, 17, 17, 17),
    "E": (31, 16, 16, 30, 16, 16, 31),
    "I": (14, 4, 4, 4, 4, 4, 14),
    "O": (14, 17, 17, 17, 17, 17, 14),
    "U": (17, 17, 17, 17, 17, 17, 14),
    "C": (14, 17, 16, 16, 16, 17, 14),
}
MARKS = {"\u0301": (2, 4), "\u0300": (8, 4),
         "\u0302": (4, 10), "\u0303": (10, 20), "\u0308": (10, 0)}


def source_rows(character: str) -> tuple[int, ...]:
    character = unicodedata.normalize("NFC", character)
    if character not in ACCENTS or len(character) != 1:
        raise ValueError("Unsupported authorial glyph")
    base, mark = unicodedata.normalize("NFD", character)
    body = BASES[base]
    if mark == "\u0327":
        return body + (4, 8)
    else:
        if base == "i":  # accented i does not keep a second dot
            body = (0, *body[1:])
        return MARKS[mark] + body


def compact_table() -> bytes:
    return b"".join(struct.pack("<H",ord(c))+bytes(source_rows(c)) for c in ACCENTS)


def bitmap(character: str, height: int) -> tuple[int, tuple[int, ...]]:
    if height not in (12,16,24,32):
        raise ValueError("Unsupported size")
    source = source_rows(character)
    width = height // 2
    # Leave one column for advance/spacing; no smoothing or source font needed.
    rows = []
    for y in range(height):
        source_row = source[y * 9 // height]
        row = 0
        for x in range(width - 1):
            if source_row & (1 << (4 - x * 5 // (width - 1))):
                row |= 1 << (width - 1 - x)
        rows.append(row)
    return width, tuple(rows)


def packed_table(height: int) -> bytes:
    result = bytearray()
    for character in ACCENTS:
        width, rows = bitmap(character, height)
        stride = math.ceil(width / 8)
        result.extend(struct.pack("<H", ord(character)))
        for row in rows:
            result.extend((row << (stride * 8 - width)).to_bytes(stride, "big"))
    return bytes(result)


def budget() -> dict:
    sizes = {height: len(packed_table(height)) for height in (12, 16, 24, 32)}
    return {"glyphs": len(ACCENTS), "bytes_by_height": sizes,
            "all_tables_bytes": sum(sizes.values()),
            "compact_source_table_bytes":len(compact_table()),
            "runtime_decoder_included": False,
            "original_font_compatible": False, "firmware_generated": False}


def preview_svg() -> str:
    parts = ['<svg xmlns="http://www.w3.org/2000/svg" width="940" height="420" viewBox="0 0 940 420">',
             '<rect width="940" height="420" fill="#111827"/>',
             '<text x="20" y="30" fill="white" font-family="sans-serif" font-size="20">Glifos PT-BR autorais · estudo de rasterização</text>']
    for index, height in enumerate((12, 16, 24, 32)):
        y = 65 + index * 85
        parts.append(f'<text x="20" y="{y+20}" fill="#67e8f9" font-family="sans-serif">{height}px</text>')
        for i, character in enumerate(ACCENTS):
            width, rows = bitmap(character, height)
            for row, mask in enumerate(rows):
                for column in range(width):
                    if mask & (1 << (width - 1 - column)):
                        parts.append(f'<rect x="{85+i*32+column}" y="{y+row}" width="1" height="1" fill="white"/>')
    parts.append('<text x="20" y="400" fill="#cbd5e1" font-family="sans-serif" font-size="14">Formato próprio; sem integração ao decodificador original. Nenhum bitmap foi extraído do equipamento.</text></svg>')
    return "".join(parts)
