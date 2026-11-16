"""Bounded authorial UTF-8 subset decoder in virtual Thumb.

Supports printable ASCII, NUL and the 26 proposed PT-BR glyphs after NFC.
This is not a general Unicode decoder or an installed text renderer.
"""
import struct

from .v14 import ACCENTS

CODE, TABLE, INPUT, RETURN = 0x10000000, 0x10001000, 0x10002000, 0x10000F00


def assemble_decoder(code_address=CODE, table_address=TABLE):
    from keystone import Ks, KS_ARCH_ARM, KS_MODE_THUMB
    source = f""".cpu cortex-m4
        push {{r4,r5,r6,lr}}
        cmp r1,#0
        beq end
        ldrb r2,[r0]
        cmp r2,#0
        beq end
        cmp r2,#32
        blo invalid
        cmp r2,#126
        bls ascii
        cmp r2,#195
        bne invalid
        cmp r1,#2
        blo invalid
        ldrb r3,[r0,#1]
        cmp r3,#128
        blo invalid
        cmp r3,#191
        bhi invalid
        and r3,r3,#63
        orr r3,r3,#192
        ldr r4, ={table_address}
        movs r5,#0
    lookup:
        ldrh r6,[r4],#2
        cmp r6,r3
        beq found
        adds r5,#1
        cmp r5,#{len(ACCENTS)}
        bne lookup
    invalid:
        movw r0,#65533
        movs r1,#1
        movs r2,#1
        rsbs r2,r2,#0
        subs r2,#1
        pop {{r4,r5,r6,pc}}
    found:
        mov r0,r3
        movs r1,#2
        mov r2,r5
        pop {{r4,r5,r6,pc}}
    ascii:
        mov r0,r2
        movs r1,#1
        movs r2,#0
        mvns r2,r2
        pop {{r4,r5,r6,pc}}
    end:
        movs r0,#0
        movs r1,#0
        movs r2,#0
        mvns r2,r2
        pop {{r4,r5,r6,pc}}
    """
    code, _ = Ks(KS_ARCH_ARM, KS_MODE_THUMB).asm(source, code_address)
    return bytes(code)


def decode(data: bytes, available: int | None = None) -> dict:
    if available is None:
        available = len(data)
    if type(available) is not int or not 0 <= available <= len(data) <= 4096:
        raise ValueError("Invalid bounded input")
    from unicorn import (Uc, UC_ARCH_ARM, UC_MODE_THUMB, UC_MODE_MCLASS,
                         UC_PROT_READ, UC_PROT_EXEC, UC_HOOK_CODE, UC_HOOK_MEM_READ,
                         UC_HOOK_MEM_WRITE)
    from unicorn import arm_const as a
    cpu = Uc(UC_ARCH_ARM, UC_MODE_THUMB | UC_MODE_MCLASS)
    cpu.ctl_set_cpu_model(a.UC_CPU_ARM_CORTEX_M4)
    cpu.mem_map(CODE,0x3000)
    cpu.mem_map(0x20000000,0x1000)
    code = assemble_decoder()
    cpu.mem_write(CODE,code)
    cpu.mem_write(TABLE,struct.pack("<"+"H"*len(ACCENTS),*[ord(c) for c in ACCENTS]))
    if data:
        cpu.mem_write(INPUT,data)
    cpu.mem_protect(CODE,0x3000,UC_PROT_READ|UC_PROT_EXEC)
    cpu.reg_write(a.UC_ARM_REG_R0,INPUT)
    cpu.reg_write(a.UC_ARM_REG_R1,available)
    cpu.reg_write(a.UC_ARM_REG_SP,0x20001000)
    cpu.reg_write(a.UC_ARM_REG_LR,RETURN|1)
    for i in range(4,12):
        cpu.reg_write(getattr(a,f"UC_ARM_REG_R{i}"),0x11110000+i)
    result = {"returned":False}

    def code_hook(engine,address,size,user):
        if address == RETURN:
            result["returned"] = True
            engine.emu_stop()
        elif not CODE <= address < CODE+len(code):
            raise RuntimeError("Decoder execution escaped")

    def read_hook(engine,access,address,size,value,user):
        if INPUT <= address < INPUT+4096 and address+size > INPUT+available:
            raise RuntimeError("Decoder read past declared input")

    def write_hook(engine,access,address,size,value,user):
        if not 0x20000F00 <= address <= 0x20001000-size:
            raise RuntimeError("Decoder write outside stack")

    cpu.hook_add(UC_HOOK_CODE,code_hook)
    cpu.hook_add(UC_HOOK_MEM_READ,read_hook)
    cpu.hook_add(UC_HOOK_MEM_WRITE,write_hook)
    cpu.emu_start(CODE|1,0,timeout=100_000,count=1000)
    if (not result["returned"] or cpu.reg_read(a.UC_ARM_REG_SP) != 0x20001000
            or any(cpu.reg_read(getattr(a,f"UC_ARM_REG_R{i}")) != 0x11110000+i for i in range(4,12))):
        raise RuntimeError("Decoder ABI failed")
    index = cpu.reg_read(a.UC_ARM_REG_R2)
    return {"codepoint":cpu.reg_read(a.UC_ARM_REG_R0),
            "consumed":cpu.reg_read(a.UC_ARM_REG_R1),
            "glyph_index":index if index < 0x80000000 else index-0x100000000,
            "code_bytes":len(code)}
