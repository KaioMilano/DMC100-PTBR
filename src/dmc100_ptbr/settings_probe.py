"""Execute only original RAM settings decode after stubbing its fetch routine.

No flash controller, save routine, USB driver or physical device is executed.
The caller supplies a synthetic, already-valid RAM buffer with magic zero.
"""
import hashlib
import struct
from .v14 import LOAD_BASE, OBSERVED_SHA256
from .arm_dispatch import LANGUAGE, STACK

BUFFER, RETURN = 0x200000A0, 0x10000000


def load_probe(firmware, words):
    if hashlib.sha256(firmware).hexdigest() != OBSERVED_SHA256:
        raise ValueError("Unknown private image")
    if len(words) != 8 or words[0] != 0 or any(type(w) is not int or not 0 <= w <= 65535 for w in words):
        raise ValueError("Requires eight synthetic uint16 words with valid zero marker")
    from unicorn import (Uc, UC_ARCH_ARM, UC_MODE_THUMB, UC_MODE_MCLASS,
                         UC_PROT_READ, UC_PROT_EXEC, UC_HOOK_CODE, UC_HOOK_MEM_WRITE)
    from unicorn import arm_const as a
    cpu = Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS)
    cpu.ctl_set_cpu_model(a.UC_CPU_ARM_CORTEX_M4)
    cpu.mem_map(0x08000000,0x20000)
    cpu.mem_map(0x20000000,0x8000)
    cpu.mem_map(RETURN,0x1000)
    cpu.mem_write(LOAD_BASE,firmware)
    packed = struct.pack("<8H",*words)
    cpu.mem_write(BUFFER,packed)
    cpu.mem_write(LANGUAGE,b"\xaa"*7)
    cpu.reg_write(a.UC_ARM_REG_SP,STACK)
    cpu.reg_write(a.UC_ARM_REG_LR,RETURN|1)
    cpu.reg_write(a.UC_ARM_REG_R4,0x12345678)
    cpu.mem_protect(0x08000000,0x20000,UC_PROT_READ|UC_PROT_EXEC)
    cpu.mem_protect(RETURN,0x1000,UC_PROT_READ|UC_PROT_EXEC)
    writes = []
    returned = False

    def write(engine,access,address,size,value,user):
        if LANGUAGE <= address and address+size <= LANGUAGE+7:
            writes.append((address,size))
        elif not STACK-0x100 <= address <= STACK-size:
            raise RuntimeError("Unexpected settings decode write")

    def code(engine,address,size,user):
        nonlocal returned
        if address == RETURN:
            returned = True
            engine.emu_stop()
        elif address == LOAD_BASE+0xB164:
            # Preserve preloaded fixture; original storage fetching not modeled.
            engine.reg_write(a.UC_ARM_REG_PC,engine.reg_read(a.UC_ARM_REG_LR))
            for i in (0,1,2,3,12):
                engine.reg_write(getattr(a,f"UC_ARM_REG_R{i}"),0xBAD00000+i)
            engine.reg_write(a.UC_ARM_REG_APSR,0xF8000000)
        elif not LOAD_BASE+0xD56C <= address < LOAD_BASE+0xD59E:
            raise RuntimeError("Execution outside settings decode")

    cpu.hook_add(UC_HOOK_CODE,code)
    cpu.hook_add(UC_HOOK_MEM_WRITE,write)
    cpu.emu_start((LOAD_BASE+0xD56C)|1,0,timeout=100_000,count=100)
    if (not returned or cpu.reg_read(a.UC_ARM_REG_SP) != STACK
            or cpu.reg_read(a.UC_ARM_REG_R4) != 0x12345678
            or bytes(cpu.mem_read(LOAD_BASE,len(firmware))) != firmware
            or bytes(cpu.mem_read(BUFFER,len(packed))) != packed):
        raise RuntimeError("Settings decode isolation failed")
    return {"decoded_bytes":list(cpu.mem_read(LANGUAGE,7)),"writes":writes,
            "flash_executed":False,"storage_fetch_stubbed":True}
