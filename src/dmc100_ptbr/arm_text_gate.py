"""Authorial text routing and emulator-only entry trampolines.

No image is emitted. The veneer reservation is outside the declared physical
flash. A branch using it must never be presented as an installable patch.
"""
import struct

GATE = 0x1000A000
OWN_TABLE = 0x1000B000
VENEER = 0x08100000
TEXT_VENEER = VENEER
MENU_VENEER = VENEER + 0x20
TEXT_TRAMP = VENEER + 0x100
MENU_TRAMP = VENEER + 0x120


def assemble(source, address):
    from keystone import Ks, KS_ARCH_ARM, KS_MODE_THUMB
    code, _ = Ks(KS_ARCH_ARM, KS_MODE_THUMB).asm(".cpu cortex-m4\n"+source,address)
    return bytes(code)


def absolute_jump(source, target):
    if source % 4:
        raise ValueError("Veneer must be word-aligned")
    return assemble(f"ldr.w pc,[pc,#0]\n.word {target|1}",source)


def entry_branch(source, target):
    if source % 2 or target % 2 or abs(target-source) >= (1 << 24)-4:
        raise ValueError("Invalid bounded Thumb branch")
    result = assemble(f"b.w #{target}",source)
    if len(result) != 4:
        raise ValueError("Expected a four-byte Thumb branch")
    return result


def gate_code(*, count, language, source_title, target_title, renderer, fallback):
    if type(count) is not int or not 0 <= count <= 128:
        raise ValueError("Invalid owned table count")
    restore = """pop {r4,r5}
        msr APSR_nzcvq,r4
        pop.w {r0,r1,r2,r3,r4,r5,r6,r7,r8,r9,r10,r11,r12,lr}
    """
    # A 64-byte frame keeps original stack arguments at +64/+68/+72.
    return assemble(f"""
        push.w {{r0,r1,r2,r3,r4,r5,r6,r7,r8,r9,r10,r11,r12,lr}}
        mrs r4,apsr
        push {{r4,r5}}
        movs r8,#0
        ldr r4, ={language}
        ldrb r4,[r4]
        cmp r4,#2
        bne lookup_start
        ldr r4, ={source_title}
        cmp r2,r4
        bne lookup_start
        ldr r2, ={target_title}
        movs r8,#1
    lookup_start:
        ldr r4, ={OWN_TABLE}
        movs r7,#{count}
    lookup:
        cbz r7,native
        subs r7,#1
        ldm r4!,{{r5,r6}}
        cmp r2,r5
        bne lookup
        ldr r4,[sp,#72]
        cmp r4,#1
        bne unsupported
        ldr r4,[sp,#68]
        cmp r4,#12
        beq owned
        cmp r4,#16
        beq owned
        cmp r4,#24
        beq owned
        cmp r4,#32
        bne unsupported
    owned:
        str r2,[sp,#16]
        str r6,[sp,#56]
        {restore}
        .balign 4
        ldr.w pc,[pc,#0]
        .word {renderer|1}
    unsupported:
        cmp r8,#0
        bne native
        {restore}
        bx lr
    native:
        {restore}
        .balign 4
        ldr.w pc,[pc,#0]
        .word {fallback|1}
    """,GATE)


def owned_table(texts):
    result = bytearray()
    if len(texts) > 128:
        raise ValueError("Too many owned buffers")
    for pointer,text in texts.items():
        data = text.encode("utf-8")
        if not 0 < pointer <= 0xffffffff or b"\0" in data or not 0 < len(data) < 32:
            raise ValueError("Owned text does not fit its declared fixed slot")
        result.extend(struct.pack("<II",pointer,len(data)+1))
    return bytes(result)
