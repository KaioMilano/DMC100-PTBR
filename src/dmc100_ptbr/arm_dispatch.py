"""Authorial Thumb dispatcher executed only in a virtual CPU.

No firmware file is patched or emitted. The additional code/data live at
artificial emulator addresses, not claimed as available on the instrument.
Optional private tests execute only the original text/glyph routines with
LCD-facing calls stubbed. They do not emulate a complete meter or certify it.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import struct

from .catalog import STRINGS
from .inspect import occurrences
from .v14 import LOAD_BASE, OBSERVED_SHA256

CODE = 0x10000000
DATA = 0x10001000
STRINGS_START = DATA + 0x800
LANGUAGE = 0x200001D8
STACK = 0x20007000
RETURN = CODE + 0xF00
TEXT = LOAD_BASE + 0x12F2
PROTECTED = frozenset({"AUTO shut_down", "Low battery", "Shutdown", "Do not use while charging"})


def private_mappings(data: bytes) -> list[tuple[int, str]]:
    if hashlib.sha256(data).hexdigest() != OBSERVED_SHA256:
        raise ValueError("Private text execution requires the observed V1.4 fingerprint")
    return [(LOAD_BASE + offset, pt) for _, en, pt in STRINGS if en not in PROTECTED
            for offset in occurrences(data, en.encode("ascii") + b"\0")]


def payload(mappings: list[tuple[int, str]]) -> tuple[bytes, dict[int, int]]:
    if len(mappings) > 128:
        raise ValueError("Too many mappings for this bounded emulator prototype")
    table = bytearray()
    strings = bytearray()
    result = {}
    shared = {}
    for pointer, text in mappings:
        if not isinstance(pointer, int) or pointer <= 0 or pointer > 0xFFFFFFFF or pointer in result:
            raise ValueError("Invalid or duplicate source pointer")
        encoded = text.encode("ascii")
        if not encoded or any(b < 32 or b > 126 for b in encoded):
            raise ValueError("This milestone permits nonempty printable ASCII drafts only")
        if encoded not in shared:
            shared[encoded] = STRINGS_START + len(strings)
            strings.extend(encoded + b"\0")
        destination = shared[encoded]
        result[pointer] = destination
        table.extend(struct.pack("<II", pointer, destination))
    if len(table) > 0x800 or len(strings) > 0x800:
        raise ValueError("Emulator payload exceeds its declared test region")
    return bytes(table).ljust(0x800, b"\0") + bytes(strings), result


def assemble(count: int) -> bytes:
    """Assemble our own wrapper into host memory; never create an image file."""
    if not 0 <= count <= 128:
        raise ValueError("Invalid bounded lookup count")
    from keystone import Ks, KS_ARCH_ARM, KS_MODE_THUMB
    source = f""".cpu cortex-m4
        push.w {{r0,r1,r3,r4,r5,r6,r7,r12,lr}}
        mrs r4, apsr
        push {{r4}}
        ldr r4, ={LANGUAGE}
        ldrb r4,[r4]
        cmp r4,#2
        bne done
        ldr r4, ={DATA}
        movs r7,#{count}
    again:
        cbz r7,done
        subs r7,#1
        ldm r4!,{{r5,r6}}
        cmp r2,r5
        bne again
        mov r2,r6
    done:
        pop {{r4}}
        msr APSR_nzcvq,r4
        pop.w {{r0,r1,r3,r4,r5,r6,r7,r12,lr}}
        .balign 4
        ldr.w pc,[pc,#0]
        .word {TEXT | 1}
    """
    code, _ = Ks(KS_ARCH_ARM, KS_MODE_THUMB).asm(source, CODE)
    return bytes(code)


def run(mappings: list[tuple[int, str]], language: int, pointer: int, *,
        firmware: bytes | None = None, wrapper: bool = True,
        stop_at_text: bool = True, height: int = 16, overlay: int = 0,
        flags: int = 0xA8000000) -> dict:
    """Run a bounded isolated test. Peripheral writes are never forwarded."""
    if not 0 <= language <= 255 or height not in (12, 16, 24, 32) or overlay not in (0, 1):
        raise ValueError("Invalid virtual test arguments")
    if firmware is not None and hashlib.sha256(firmware).hexdigest() != OBSERVED_SHA256:
        raise ValueError("Unknown private image")
    if not stop_at_text and firmware is None:
        raise ValueError("Original routine execution requires a private observed image")
    from unicorn import (Uc, UC_ARCH_ARM, UC_MODE_THUMB, UC_MODE_MCLASS, UC_PROT_READ,
                         UC_PROT_EXEC, UC_HOOK_CODE, UC_HOOK_MEM_WRITE)
    from unicorn import arm_const as a
    registers = [getattr(a, f"UC_ARM_REG_R{i}") for i in range(13)]
    uc = Uc(UC_ARCH_ARM, UC_MODE_THUMB | UC_MODE_MCLASS)
    uc.ctl_set_cpu_model(a.UC_CPU_ARM_CORTEX_M4)
    uc.mem_map(0x08000000, 0x20000)
    uc.mem_map(0x20000000, 0x8000)
    uc.mem_map(CODE, 0x1000)
    uc.mem_map(DATA, 0x2000)
    content, destinations = payload(mappings)
    code = assemble(len(mappings))
    uc.mem_write(CODE, code)
    uc.mem_write(DATA, content)
    if firmware is not None:
        uc.mem_write(LOAD_BASE, firmware)
    uc.mem_write(LANGUAGE, bytes([language]))
    for i, reg in enumerate(registers):
        uc.reg_write(reg, 0x11110000 + i)
    for reg, value in ((a.UC_ARM_REG_R0, 10), (a.UC_ARM_REG_R1, 20),
                       (a.UC_ARM_REG_R2, pointer), (a.UC_ARM_REG_R3, 0xF79E),
                       (a.UC_ARM_REG_SP, STACK), (a.UC_ARM_REG_LR, RETURN | 1)):
        uc.reg_write(reg, value)
    uc.reg_write(a.UC_ARM_REG_APSR, flags)
    arguments = struct.pack("<III", 0x0841, height, overlay)
    uc.mem_write(STACK, arguments)
    initial_registers = [uc.reg_read(r) for r in registers]
    initial_flags = uc.reg_read(a.UC_ARM_REG_APSR)
    uc.mem_protect(0x08000000, 0x20000, UC_PROT_READ | UC_PROT_EXEC)
    uc.mem_protect(CODE, 0x1000, UC_PROT_READ | UC_PROT_EXEC)
    uc.mem_protect(DATA, 0x2000, UC_PROT_READ)
    trace = hashlib.sha256()
    counts = {"windows": 0, "data16": 0, "pixels": 0}
    result = {"reached_text": False, "returned": False, "unexpected_writes": [],
              "unexpected_execution": [], "stack_argument_bytes_preserved": False}

    def on_write(engine, access, address, size, value, user):
        if not STACK - 0x800 <= address <= STACK + 12 - size:
            result["unexpected_writes"].append({"address": address, "size": size})
            engine.emu_stop()

    def on_code(engine, address, size, user):
        if address == TEXT and not result["reached_text"]:
            now = [engine.reg_read(r) for r in registers]
            result.update({"reached_text": True, "selected_pointer": now[2],
                           "registers_preserved_except_r2": all(x == y for i, (x, y) in enumerate(zip(initial_registers, now)) if i != 2),
                           "flags_preserved": engine.reg_read(a.UC_ARM_REG_APSR) == initial_flags,
                           "sp_preserved_at_entry": engine.reg_read(a.UC_ARM_REG_SP) == STACK,
                           "lr_preserved_at_entry": engine.reg_read(a.UC_ARM_REG_LR) == RETURN | 1,
                           "stack_argument_bytes_preserved": bytes(engine.mem_read(STACK, 12)) == arguments})
            if stop_at_text:
                engine.emu_stop()
                return
        if address == RETURN:
            result["returned"] = True
            engine.emu_stop()
            return
        window, data16, pixel = [LOAD_BASE + offset for offset in (0xAFA, 0x1AB8, 0xDBA)]
        if address in (window, data16, pixel):
            r = [engine.reg_read(reg) for reg in registers[:4]]
            if address == window:
                trace.update(struct.pack("<BIIII", 0, *r)); counts["windows"] += 1
            elif address == data16:
                trace.update(struct.pack("<BH", 1, r[0] & 0xFFFF)); counts["data16"] += 1
            else:
                trace.update(struct.pack("<BIII", 2, r[0], r[1], r[2])); counts["pixels"] += 1
            engine.reg_write(a.UC_ARM_REG_PC, engine.reg_read(a.UC_ARM_REG_LR))
            return
        allowed = CODE <= address < CODE + len(code) or LOAD_BASE + 0x12F2 <= address < LOAD_BASE + 0x1AB8
        if not allowed:
            result["unexpected_execution"].append(address)
            engine.emu_stop()

    uc.hook_add(UC_HOOK_MEM_WRITE, on_write)
    uc.hook_add(UC_HOOK_CODE, on_code)
    uc.emu_start((CODE if wrapper else TEXT) | 1, 0, timeout=5_000_000, count=2_000_000)
    result.update({"trace_sha256": trace.hexdigest(), "trace_counts": counts,
                   "original_rom_unchanged": firmware is None or bytes(uc.mem_read(LOAD_BASE, len(firmware))) == firmware,
                   "final_sp": uc.reg_read(a.UC_ARM_REG_SP),
                   "final_language": uc.mem_read(LANGUAGE, 1)[0],
                   "code_bytes": len(code), "table_bytes": 8 * len(mappings),
                   "translation_bytes": len(content) - 0x800})
    return result


def compare_private(firmware: bytes) -> dict:
    mappings = private_mappings(firmware)
    _, destinations = payload(mappings)
    abi_checks = 0
    for language in (0, 1, 2, 255):
        for pointer, _ in mappings:
            result = run(mappings, language, pointer)
            expected = destinations[pointer] if language == 2 else pointer
            if result.get("selected_pointer") != expected or not all(result.get(key) for key in (
                    "registers_preserved_except_r2", "flags_preserved", "sp_preserved_at_entry",
                    "lr_preserved_at_entry", "stack_argument_bytes_preserved")):
                raise RuntimeError("ARM entry contract failed")
            abi_checks += 1
    comparisons = 0
    for language in (0, 1, 2):
        for pointer, _ in mappings:
            selected = destinations[pointer] if language == 2 else pointer
            expected = run(mappings, language, selected, firmware=firmware, wrapper=False, stop_at_text=False)
            actual = run(mappings, language, pointer, firmware=firmware, stop_at_text=False)
            for value in (expected, actual):
                if not value["returned"] or value["final_sp"] != STACK or value["unexpected_writes"] or value["unexpected_execution"] or not value["original_rom_unchanged"]:
                    raise RuntimeError("Text execution escaped its test contract")
            if expected["trace_sha256"] != actual["trace_sha256"] or expected["trace_counts"] != actual["trace_counts"]:
                raise RuntimeError("LCD-facing trace differs from expected original routine")
            comparisons += 1
    return {"scope": "Virtual Cortex-M4 text entry and original glyph path; LCD calls stubbed",
            "mapped_occurrences": len(mappings), "abi_checks": abi_checks,
            "original_text_trace_comparisons": comparisons,
            "code_bytes": len(assemble(len(mappings))), "table_bytes": len(mappings) * 8,
            "translation_bytes": len(payload(mappings)[0]) - 0x800,
            "protected_messages_omitted": sorted(PROTECTED),
            "firmware_generated": False, "installable_ready": False,
            "sha256": hashlib.sha256(firmware).hexdigest()}


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--firmware", type=Path, required=True, help="Private observed image, read-only")
    args = parser.parse_args(argv)
    try:
        before = args.firmware.read_bytes()
        report = compare_private(before)
        if args.firmware.read_bytes() != before:
            raise RuntimeError("Private input changed")
    except (OSError, ValueError, RuntimeError, ImportError) as exc:
        parser.error(str(exc))
    print(json.dumps(report, indent=2))
    return 0  # the emulation experiment passed; never installation approval


if __name__ == "__main__":
    raise SystemExit(main())
