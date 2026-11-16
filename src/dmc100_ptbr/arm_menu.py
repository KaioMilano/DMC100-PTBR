"""Authorial three-language selector in virtual ARM; no original menu patched.

Registers r0/r1/r2 carry active language, cursor and confirmation state.
r3 carries UP=0, DOWN=1, OK=2 or BACK=3. No flash or device access exists.
"""
from __future__ import annotations

import argparse
import json

ADDRESS = 0x10000000
RETURN = ADDRESS + 0xF00
LANGUAGES = ("Chinês", "English", "Português (BR)")
EVENTS = {"up": 0, "down": 1, "ok": 2, "back": 3}


def assemble_menu() -> bytes:
    from keystone import Ks, KS_ARCH_ARM, KS_MODE_THUMB
    # Deliberately independent of the proprietary UI, storage and rendering.
    source = """.cpu cortex-m4
        cmp r3,#0
        beq up
        cmp r3,#1
        beq down
        cmp r3,#2
        beq ok
        cmp r3,#3
        bne done
        mov r1,r0
        movs r2,#0
        bx lr
    up:
        movs r2,#0
        cmp r1,#0
        bne decrement
        movs r1,#2
        bx lr
    decrement:
        subs r1,#1
        bx lr
    down:
        movs r2,#0
        cmp r1,#2
        bne increment
        movs r1,#0
        bx lr
    increment:
        adds r1,#1
        bx lr
    ok:
        cmp r2,#0
        bne commit
        movs r2,#1
        bx lr
    commit:
        mov r0,r1
        movs r2,#0
    done:
        bx lr
    """
    code, _ = Ks(KS_ARCH_ARM, KS_MODE_THUMB).asm(source, ADDRESS)
    return bytes(code)


def step(state: tuple[int, int, int], event: str) -> dict:
    if (len(state) != 3 or any(type(value) is not int for value in state)
            or state[0] not in range(3) or state[1] not in range(3)
            or state[2] not in (0, 1) or event not in EVENTS):
        raise ValueError("Invalid virtual selector state or event")
    from unicorn import (Uc, UC_ARCH_ARM, UC_MODE_THUMB, UC_MODE_MCLASS,
                         UC_PROT_READ, UC_PROT_EXEC, UC_HOOK_CODE)
    from unicorn import arm_const as a
    cpu = Uc(UC_ARCH_ARM, UC_MODE_THUMB | UC_MODE_MCLASS)
    cpu.ctl_set_cpu_model(a.UC_CPU_ARM_CORTEX_M4)
    cpu.mem_map(ADDRESS, 0x1000)
    code = assemble_menu()
    cpu.mem_write(ADDRESS, code)
    cpu.mem_protect(ADDRESS, 0x1000, UC_PROT_READ | UC_PROT_EXEC)
    registers = [getattr(a, f"UC_ARM_REG_R{i}") for i in range(13)]
    for i, register in enumerate(registers):
        cpu.reg_write(register, 0x11110000 + i)
    for register, value in zip(registers[:4], (*state, EVENTS[event])):
        cpu.reg_write(register, value)
    cpu.reg_write(a.UC_ARM_REG_SP, 0x20007000)
    cpu.reg_write(a.UC_ARM_REG_LR, RETURN | 1)
    canaries = [cpu.reg_read(r) for r in registers[3:]]
    result = {"returned": False}

    def hook(engine, address, size, user):
        if address == RETURN:
            result["returned"] = True
            engine.emu_stop()
        elif not ADDRESS <= address < ADDRESS + len(code):
            raise RuntimeError("Selector escaped authorial code")

    cpu.hook_add(UC_HOOK_CODE, hook)
    cpu.emu_start(ADDRESS | 1, 0, timeout=100_000, count=100)
    preserved = ([cpu.reg_read(r) for r in registers[3:]] == canaries
                 and cpu.reg_read(a.UC_ARM_REG_SP) == 0x20007000
                 and cpu.reg_read(a.UC_ARM_REG_LR) == RETURN | 1)
    if not result["returned"] or not preserved:
        raise RuntimeError("Selector failed its virtual execution contract")
    result.update(state=tuple(cpu.reg_read(r) for r in registers[:3]),
                  preserved_registers=True, code_bytes=len(code))
    return result


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("events", nargs="*", metavar="{up,down,ok,back}")
    args = parser.parse_args(argv)
    if any(event not in EVENTS for event in args.events):
        parser.error("Events must be up, down, ok or back")
    state = (1, 1, 0)
    events = args.events or ["down", "ok", "ok"]
    trace = []
    for event in events:
        result = step(state, event)
        state = result["state"]
        trace.append({"event": event, "active": LANGUAGES[state[0]],
                      "cursor": LANGUAGES[state[1]], "confirmation": bool(state[2])})
    print(json.dumps({"scope": "Authorial virtual ARM selector, not original menu",
                      "trace": trace, "flash_written": False,
                      "firmware_generated": False}, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
