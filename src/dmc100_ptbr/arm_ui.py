"""Integrated authorial language UI in one virtual CPU, optionally over V1.4.

All additional addresses and the cursor state region are emulator-only.
Events are injected by the host, not decoded from physical buttons. No file is
patched, no flash is written, and drawing calls remain intercepted.
"""
import hashlib
import struct

from .arm_menu import ADDRESS as SELECTOR, EVENTS, assemble_menu
from .arm_dispatch import LANGUAGE, STACK
from .original_menu import CALLS, ENTRY_OFFSET, END_OFFSET
from .v14 import LOAD_BASE, OBSERVED_SHA256
from .v14 import ACCENTS
from .accent_font import compact_table
from .arm_utf8 import assemble_decoder

BRIDGE = 0x10002000
DRAW = 0x10003000
DATA = 0x10004000
RETURN = 0x1000F000
STATE = 0x20001000  # artificial test reservation; NOT free RAM on the meter
PT = DATA + 0x100
TITLE = DATA + 0x120
CONFIRM = DATA + 0x140
DECODER, KEYS, FONT, RENDERER = 0x10005000, 0x10006000, 0x10007000, 0x10009000
OWN_TEXTS = {PT: "Português (BR)", TITLE: "Idioma", CONFIRM: "Confirmar?"}


def _assemble(source, address):
    from keystone import Ks, KS_ARCH_ARM, KS_MODE_THUMB
    code, _ = Ks(KS_ARCH_ARM, KS_MODE_THUMB).asm(".cpu cortex-m4\n" + source, address)
    return bytes(code)


def bridge_code():
    # Direct ARM-to-ARM call: host does not shuttle the three state registers.
    return _assemble(f"""
        push {{r4,r5,r6,lr}}
        ldr r4, ={STATE}
        ldm r4,{{r0,r1,r2}}
        ldr r5, ={SELECTOR | 1}
        blx r5
        stm r4,{{r0,r1,r2}}
        ldr r5, ={LANGUAGE}
        strb r0,[r5]
        pop {{r4,r5,r6,pc}}
    """, BRIDGE)


def draw_code():
    def call(offset):
        return f"ldr r12, ={(LOAD_BASE + offset) | 1}\n blx r12"
    return _assemble(f"""
        push.w {{r4,r5,r6,r7,r8,lr}}
        sub sp,#16
        {call(ENTRY_OFFSET)}
        ldr r4, ={LANGUAGE - 6}
        ldrh r5,[r4]
        ldrh r4,[r4,#2]
        str r5,[sp]
        movs r0,#40
        movs r1,#185
        movs r2,#220
        movw r3,#310
        {call(0xF24)}
        ldr r6, ={STATE}
        ldr r6,[r6,#8]
        cmp r6,#0
        beq rows
        movs r0,#45
        movs r1,#150
        movs r2,#220
        movs r3,#180
        str r5,[sp]
        {call(0xF24)}
        movs r0,#75
        movs r1,#158
        ldr r2, ={CONFIRM}
        mov r3,r4
        str r5,[sp]
        movs r6,#16
        str r6,[sp,#4]
        movs r6,#1
        str r6,[sp,#8]
        {call(0x12F2)}
    rows:
        movs r6,#0
        ldr r7, ={DATA}
        movs r8,#200
    row:
        ldr r0, ={STATE}
        ldr r0,[r0,#4]
        cmp r0,r6
        bne checkbox
        movs r0,#97
        sub r1,r8,#2
        movs r2,#218
        add r3,r8,#23
        str r4,[sp]
        {call(0xE44)}
    checkbox:
        movs r0,#65
        mov r1,r8
        movs r2,#85
        add r3,r8,#20
        str r4,[sp]
        ldr r12, ={LANGUAGE}
        ldrb r12,[r12]
        cmp r12,r6
        bne outline
        {call(0xF24)}
        b label
    outline:
        {call(0xE44)}
    label:
        movs r0,#106
        add r1,r8,#1
        ldr r2,[r7],#4
        mov r3,r4
        str r5,[sp]
        movs r12,#16
        str r12,[sp,#4]
        movs r12,#1
        str r12,[sp,#8]
        {call(0x12F2)}
        adds r6,#1
        add r8,r8,#36
        cmp r6,#3
        bne row
        add sp,#16
        pop.w {{r4,r5,r6,r7,r8,pc}}
    """, DRAW)


def renderer_code():
    # Prototype ABI: original text arguments plus r12=known authorial buffer
    # length, supplied by the emulator seam. Height 12/16/24/32, overlay=1.
    return _assemble(f"""
        push.w {{r4,r5,r6,r7,r8,r9,r10,r11,lr}}
        sub sp,#36
        mov r4,r0
        mov r5,r1
        mov r6,r2
        mov r7,r3
        mov r8,r12
        ldr r9,[sp,#72]
        ldr r0,[sp,#76]
        str r0,[sp,#20]
        lsrs r0,r0,#1
        str r0,[sp,#24]
    next:
        cmp r8,#0
        beq finished
        mov r0,r6
        mov r1,r8
        ldr r12, ={DECODER | 1}
        blx r12
        add r6,r6,r1
        sub r8,r8,r1
        cmp r0,#0
        beq finished
        cmp r2,#0
        bge accent
        cmp r0,#127
        bls ascii
        movs r0,#63
    ascii:
        strh r0,[sp,#12]
        mov r0,r4
        mov r1,r5
        add r2,sp,#12
        mov r3,r7
        str r9,[sp]
        ldr r12,[sp,#20]
        str r12,[sp,#4]
        movs r12,#1
        str r12,[sp,#8]
        ldr r12, ={(LOAD_BASE + 0x12F2) | 1}
        blx r12
        b advance
    accent:
        movs r0,#11
        mul r10,r2,r0
        ldr r0, ={FONT + 2}
        add r10,r10,r0
        movs r11,#0
    scanrow:
        movs r0,#9
        mul r0,r11,r0
        ldr r1,[sp,#20]
        udiv r0,r0,r1
        ldrb r0,[r10,r0]
        str r0,[sp,#16]
        movs r0,#0
        str r0,[sp,#12]
    scancol:
        ldr r3,[sp,#12]
        movs r0,#5
        mul r0,r3,r0
        ldr r1,[sp,#24]
        subs r1,#1
        udiv r0,r0,r1
        movs r1,#16
        lsr r0,r1,r0
        ldr r12,[sp,#16]
        tst r12,r0
        beq skip
        add r0,r4,r3
        cmp r0,#240
        bhs skip
        add r1,r5,r11
        movw r2,#320
        cmp r1,r2
        bhs skip
        mov r2,r7
        ldr r12, ={(LOAD_BASE + 0xDBA) | 1}
        blx r12
    skip:
        ldr r0,[sp,#12]
        adds r0,#1
        str r0,[sp,#12]
        ldr r1,[sp,#24]
        subs r1,#1
        cmp r0,r1
        bne scancol
        add r11,r11,#1
        ldr r0,[sp,#20]
        cmp r11,r0
        bne scanrow
    advance:
        ldr r0,[sp,#24]
        add r4,r4,r0
        b next
    finished:
        add sp,#36
        pop.w {{r4,r5,r6,r7,r8,r9,r10,r11,pc}}
    """, RENDERER)


class VirtualLanguageUI:
    def __init__(self, firmware=None, language=1, execute_glyphs=False):
        if type(language) is not int or language not in range(3):
            raise ValueError("Unsupported initial locale")
        if firmware is not None and hashlib.sha256(firmware).hexdigest() != OBSERVED_SHA256:
            raise ValueError("Unknown private image")
        if execute_glyphs and firmware is None:
            raise ValueError("Original glyph execution requires private observed image")
        from unicorn import (Uc, UC_ARCH_ARM, UC_MODE_THUMB, UC_MODE_MCLASS,
                             UC_PROT_READ, UC_PROT_EXEC, UC_HOOK_CODE, UC_HOOK_MEM_WRITE)
        from unicorn import arm_const as a
        self.a, self.firmware, self.trace = a, firmware, []
        self.execute_glyphs = execute_glyphs
        self.cpu = cpu = Uc(UC_ARCH_ARM, UC_MODE_THUMB | UC_MODE_MCLASS)
        cpu.ctl_set_cpu_model(a.UC_CPU_ARM_CORTEX_M4)
        cpu.mem_map(0x08000000, 0x20000)
        cpu.mem_map(0x20000000, 0x8000)
        cpu.mem_map(0x10000000, 0x10000)
        if firmware is not None:
            cpu.mem_write(LOAD_BASE, firmware)
        self.ranges = []
        for address, code in ((SELECTOR, assemble_menu()), (BRIDGE, bridge_code()), (DRAW, draw_code()),
                              (DECODER, assemble_decoder(DECODER, KEYS)), (RENDERER, renderer_code())):
            cpu.mem_write(address, code)
            self.ranges.append((address, address + len(code)))
        self.renderer_end = next(hi for lo, hi in self.ranges if lo == RENDERER)
        cpu.mem_write(DATA, struct.pack("<III", LOAD_BASE + 0x5A50, LOAD_BASE + 0x5A5C, PT))
        for address, text in OWN_TEXTS.items():
            cpu.mem_write(address, text.encode("utf-8") + b"\0")
        cpu.mem_write(KEYS, struct.pack("<"+"H"*len(ACCENTS), *map(ord, ACCENTS)))
        cpu.mem_write(FONT, compact_table())
        cpu.mem_write(STATE, struct.pack("<III", language, language, 0))
        cpu.mem_write(LANGUAGE, bytes([language]))
        cpu.mem_write(LANGUAGE - 6, struct.pack("<HH", 0xFFFF, 0))
        cpu.mem_protect(0x08000000, 0x20000, UC_PROT_READ | UC_PROT_EXEC)
        cpu.mem_protect(0x10000000, 0x10000, UC_PROT_READ | UC_PROT_EXEC)
        cpu.hook_add(UC_HOOK_CODE, self._code)
        cpu.hook_add(UC_HOOK_MEM_WRITE, self._write)
        self.returned = False
        self.operation = None

    def _write(self, cpu, access, address, size, value, user):
        in_stack = STACK - 0x800 <= address <= STACK - size
        in_state = STATE <= address and address + size <= STATE + 12
        language = address == LANGUAGE and size == 1
        if not (in_stack or self.operation == "event" and (in_state or language)):
            raise RuntimeError("Unexpected virtual write")

    def _code(self, cpu, address, size, user):
        a = self.a
        if address == RETURN:
            self.returned = True
            cpu.emu_stop()
            return
        offset = address - LOAD_BASE
        if offset == ENTRY_OFFSET and self.redirect:
            self.redirect = False
            cpu.reg_write(a.UC_ARM_REG_PC, DRAW | 1)
            return
        if offset == ENTRY_OFFSET and self.firmware is None:
            # Public synthetic seam, never described as execution of V1.4.
            cpu.reg_write(a.UC_ARM_REG_PC, cpu.reg_read(a.UC_ARM_REG_LR))
            return
        if offset in (0xAFA, 0x1AB8, 0xDBA):
            lr = cpu.reg_read(a.UC_ARM_REG_LR) & ~1
            own_accent = offset == 0xDBA and RENDERER <= lr < self.renderer_end
            if not own_accent:
                regs = [cpu.reg_read(getattr(a, f"UC_ARM_REG_R{i}")) for i in range(4)]
                self.native_hash.update(struct.pack("<IIIII", offset, *regs))
                self.native_calls += 1
                cpu.reg_write(a.UC_ARM_REG_PC, cpu.reg_read(a.UC_ARM_REG_LR))
                return
        if offset in CALLS or offset == 0xDBA:
            regs = [cpu.reg_read(getattr(a, f"UC_ARM_REG_R{i}")) for i in range(4)]
            if offset == 0x12F2 and regs[2] == LOAD_BASE + 0x5A44 and self.state[0] == 2:
                regs[2] = TITLE
                cpu.reg_write(a.UC_ARM_REG_R2, TITLE)
            extra = list(struct.unpack("<III", cpu.mem_read(cpu.reg_read(a.UC_ARM_REG_SP), 12)))
            call = CALLS.get(offset, "accent_pixel")
            if offset == 0x12F2 and regs[2] in OWN_TEXTS:
                if extra[1] not in (12,16,24,32) or extra[2] != 1:
                    raise RuntimeError("Unsupported authorial font size or overlay")
                extra[1] = self.authorial_height
                cpu.mem_write(cpu.reg_read(a.UC_ARM_REG_SP)+4, struct.pack("<I",extra[1]))
                self.trace.append({"call": "text", "args": regs, "stack_args": extra})
                cpu.reg_write(a.UC_ARM_REG_R12, len(OWN_TEXTS[regs[2]].encode("utf-8"))+1)
                cpu.reg_write(a.UC_ARM_REG_PC, RENDERER | 1)
                return
            if offset == 0x12F2 and STACK-0x800 <= regs[2] < STACK:
                call = "ascii_fragment"
            self.trace.append({"call": call, "args": regs, "stack_args": extra})
            if offset == 0x12F2 and self.execute_glyphs:
                return  # execute original text/glif code, only LCD boundary stubbed
            cpu.reg_write(a.UC_ARM_REG_PC, cpu.reg_read(a.UC_ARM_REG_LR))
            # Model volatile argument registers/flags as clobbered so callers
            # cannot accidentally depend on a Python stub preserving them.
            for i in (0, 1, 2, 3, 12):
                cpu.reg_write(getattr(a, f"UC_ARM_REG_R{i}"), 0xBAD00000 + i)
            cpu.reg_write(a.UC_ARM_REG_APSR, 0xF8000000)
            return
        allowed = any(lo <= address < hi for lo, hi in self.ranges)
        allowed |= self.firmware is not None and ENTRY_OFFSET <= offset < END_OFFSET
        allowed |= self.execute_glyphs and LOAD_BASE+0x12F2 <= address < LOAD_BASE+0x1AB8
        if not allowed:
            raise RuntimeError("Unexpected virtual execution")

    @property
    def state(self):
        return struct.unpack("<III", self.cpu.mem_read(STATE, 12))

    def _run(self, address, operation, event=0, redirect=False):
        a, cpu = self.a, self.cpu
        self.trace, self.returned, self.operation, self.redirect = [], False, operation, redirect
        self.native_hash, self.native_calls = hashlib.sha256(), 0
        for i in range(13):
            cpu.reg_write(getattr(a, f"UC_ARM_REG_R{i}"), 0x11110000 + i)
        cpu.reg_write(a.UC_ARM_REG_R3, event)
        cpu.reg_write(a.UC_ARM_REG_SP, STACK)
        cpu.reg_write(a.UC_ARM_REG_LR, RETURN | 1)
        saved = [cpu.reg_read(getattr(a, f"UC_ARM_REG_R{i}")) for i in range(4, 12)]
        cpu.emu_start(address | 1, 0, timeout=5_000_000, count=2_000_000)
        if (not self.returned or cpu.reg_read(a.UC_ARM_REG_SP) != STACK
                or saved != [cpu.reg_read(getattr(a, f"UC_ARM_REG_R{i}")) for i in range(4, 12)]
                or cpu.mem_read(LANGUAGE, 1)[0] != self.state[0]):
            raise RuntimeError("Integrated UI contract failed")
        if self.firmware is not None and bytes(cpu.mem_read(LOAD_BASE, len(self.firmware))) != self.firmware:
            raise RuntimeError("Original virtual ROM changed")
        return {"state": self.state, "trace": list(self.trace),
                "original_menu_executed": self.firmware is not None and operation == "render",
                "original_glyph_boundary_calls": self.native_calls,
                "original_glyph_trace_sha256": self.native_hash.hexdigest(),
                "firmware_generated": False, "installable_ready": False}

    def event(self, name):
        if name not in EVENTS:
            raise ValueError("Unsupported virtual event")
        return self._run(BRIDGE, "event", EVENTS[name])

    def render(self, authorial_height=16):
        if authorial_height not in (12,16,24,32):
            raise ValueError("Unsupported authorial height")
        self.authorial_height = authorial_height
        # CPU hook redirects original entry only for this top-level call. The
        # authorial wrapper calls the unchanged original, then redraws rows.
        return self._run(LOAD_BASE + ENTRY_OFFSET, "render", redirect=True)
