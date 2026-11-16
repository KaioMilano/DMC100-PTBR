"""Read-only virtual execution of the fingerprint-bound original language menu.

Draw calls are intercepted before drivers or glyphs run. This characterizes the
two-choice original layout, not a complete device or a patched firmware.
"""
import argparse
import hashlib
import json
from pathlib import Path
import struct

from .arm_dispatch import LANGUAGE, STACK
from .v14 import LOAD_BASE, OBSERVED_SHA256

ENTRY_OFFSET = 0x5938
END_OFFSET = 0x5A3C
RETURN = 0x10000000
CALLS = {0xF24: "fill", 0xC6C: "arc", 0x72E0: "tab_dots",
         0x12F2: "text", 0xE88: "rounded_rectangle", 0xE44: "outline"}


def run_menu(firmware: bytes, language: int) -> dict:
    if hashlib.sha256(firmware).hexdigest() != OBSERVED_SHA256:
        raise ValueError("Requires the observed private V1.4 fingerprint")
    if type(language) is not int or not 0 <= language <= 255:
        raise ValueError("Invalid language byte")
    from unicorn import (Uc, UC_ARCH_ARM, UC_MODE_THUMB, UC_MODE_MCLASS,
                         UC_PROT_READ, UC_PROT_EXEC, UC_HOOK_CODE, UC_HOOK_MEM_WRITE)
    from unicorn import arm_const as a
    cpu = Uc(UC_ARCH_ARM, UC_MODE_THUMB | UC_MODE_MCLASS)
    cpu.ctl_set_cpu_model(a.UC_CPU_ARM_CORTEX_M4)
    cpu.mem_map(0x08000000, 0x20000)
    cpu.mem_map(0x20000000, 0x8000)
    cpu.mem_map(RETURN, 0x1000)
    cpu.mem_write(LOAD_BASE, firmware)
    cpu.mem_write(LANGUAGE, bytes([language]))
    cpu.mem_write(LANGUAGE - 6, struct.pack("<HH", 0xFFFF, 0x0000))
    registers = [getattr(a, f"UC_ARM_REG_R{i}") for i in range(13)]
    for i, reg in enumerate(registers):
        cpu.reg_write(reg, 0x11110000 + i)
    cpu.reg_write(a.UC_ARM_REG_SP, STACK)
    cpu.reg_write(a.UC_ARM_REG_LR, RETURN | 1)
    saved = [cpu.reg_read(r) for r in registers[4:12]]
    cpu.mem_protect(0x08000000, 0x20000, UC_PROT_READ | UC_PROT_EXEC)
    cpu.mem_protect(RETURN, 0x1000, UC_PROT_READ | UC_PROT_EXEC)
    trace = []
    returned = False
    unexpected = []

    def on_write(engine, access, address, size, value, user):
        if not STACK - 0x800 <= address <= STACK - size:
            unexpected.append("write_outside_stack")
            engine.emu_stop()

    def on_code(engine, address, size, user):
        nonlocal returned
        if address == RETURN:
            returned = True
            engine.emu_stop()
            return
        offset = address - LOAD_BASE
        if offset in CALLS:
            args = [engine.reg_read(r) for r in registers[:4]]
            stack = engine.reg_read(a.UC_ARM_REG_SP)
            # Only text has three inspected stack arguments. No proprietary
            # text, font or pixel bytes leave the virtual address space.
            extra = list(struct.unpack("<III", engine.mem_read(stack, 12))) if offset == 0x12F2 else []
            trace.append({"call": CALLS[offset], "args": args, "stack_args": extra})
            engine.reg_write(a.UC_ARM_REG_PC, engine.reg_read(a.UC_ARM_REG_LR))
        elif not ENTRY_OFFSET <= offset < END_OFFSET:
            unexpected.append("execution_outside_menu")
            engine.emu_stop()

    cpu.hook_add(UC_HOOK_CODE, on_code)
    cpu.hook_add(UC_HOOK_MEM_WRITE, on_write)
    cpu.emu_start((LOAD_BASE + ENTRY_OFFSET) | 1, 0, timeout=100_000, count=1000)
    intact = bytes(cpu.mem_read(LOAD_BASE, len(firmware))) == firmware
    if (not returned or unexpected or not intact
            or cpu.reg_read(a.UC_ARM_REG_SP) != STACK
            or saved != [cpu.reg_read(r) for r in registers[4:12]]
            or cpu.mem_read(LANGUAGE, 1)[0] != language):
        raise RuntimeError("Original menu failed virtual isolation contract")
    return {"language": language, "trace": trace, "returned": returned,
            "rom_unchanged": intact, "language_unchanged": True,
            "draw_calls_stubbed": True, "firmware_generated": False}


def compare(firmware: bytes) -> dict:
    results = {locale: run_menu(firmware, locale) for locale in (0, 1, 2, 255)}
    return {"sha256": hashlib.sha256(firmware).hexdigest(),
            "scope": "Original V1.4 menu CPU execution; drawing calls stubbed",
            "menu_offset_hex": "0x005938",
            "languages_tested": list(results),
            "ptbr_byte_matches_english_trace": results[2]["trace"] == results[1]["trace"],
            "invalid_byte_matches_english_trace": results[255]["trace"] == results[1]["trace"],
            "chinese_differs_from_english": results[0]["trace"] != results[1]["trace"],
            "text_calls_per_locale": {str(k): sum(t["call"] == "text" for t in r["trace"])
                                      for k, r in results.items()},
            "original_rom_unchanged": all(r["rom_unchanged"] for r in results.values()),
            "third_option_in_original_menu": False,
            "firmware_generated": False, "installable_ready": False}


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("firmware", type=Path)
    args = parser.parse_args(argv)
    data = args.firmware.read_bytes()
    report = compare(data)
    if args.firmware.read_bytes() != data:
        raise RuntimeError("Private input changed")
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
