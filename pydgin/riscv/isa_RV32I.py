# =======================================================================
# isa_RV32I.py
# =======================================================================
'RISC-V instructions for base integer instruction set.'

from pydgin.misc import NotImplementedInstError
from pydgin.riscv.helpers import *
from pydgin.riscv.utils import sext_xlen, sext_32, sext, signed, trim
from pydgin.utils import trim_32

# =======================================================================
# Instruction Encodings
# =======================================================================

encodings = [

    ['lui', 'xxxxxxxxxxxxxxxxxxxxxxxxx0110111'],
    ['auipc', 'xxxxxxxxxxxxxxxxxxxxxxxxx0010111'],
    ['jal', 'xxxxxxxxxxxxxxxxxxxxxxxxx1101111'],
    ['jalr', 'xxxxxxxxxxxxxxxxx000xxxxx1100111'],
    ['beq', 'xxxxxxxxxxxxxxxxx000xxxxx1100011'],
    ['bne', 'xxxxxxxxxxxxxxxxx001xxxxx1100011'],
    ['blt', 'xxxxxxxxxxxxxxxxx100xxxxx1100011'],
    ['bge', 'xxxxxxxxxxxxxxxxx101xxxxx1100011'],
    ['bltu', 'xxxxxxxxxxxxxxxxx110xxxxx1100011'],
    ['bgeu', 'xxxxxxxxxxxxxxxxx111xxxxx1100011'],
    ['lb', 'xxxxxxxxxxxxxxxxx000xxxxx0000011'],
    ['lh', 'xxxxxxxxxxxxxxxxx001xxxxx0000011'],
    ['lw', 'xxxxxxxxxxxxxxxxx010xxxxx0000011'],
    ['lbu', 'xxxxxxxxxxxxxxxxx100xxxxx0000011'],
    ['lhu', 'xxxxxxxxxxxxxxxxx101xxxxx0000011'],
    ['sb', 'xxxxxxxxxxxxxxxxx000xxxxx0100011'],
    ['sh', 'xxxxxxxxxxxxxxxxx001xxxxx0100011'],
    ['sw', 'xxxxxxxxxxxxxxxxx010xxxxx0100011'],
    ['addi', 'xxxxxxxxxxxxxxxxx000xxxxx0010011'],
    ['slti', 'xxxxxxxxxxxxxxxxx010xxxxx0010011'],
    ['sltiu', 'xxxxxxxxxxxxxxxxx011xxxxx0010011'],
    ['xori', 'xxxxxxxxxxxxxxxxx100xxxxx0010011'],
    ['ori', 'xxxxxxxxxxxxxxxxx110xxxxx0010011'],
    ['andi', 'xxxxxxxxxxxxxxxxx111xxxxx0010011'],
    ['slli', '000000xxxxxxxxxxx001xxxxx0010011'],
    ['srli', '000000xxxxxxxxxxx101xxxxx0010011'],
    ['srai', '010000xxxxxxxxxxx101xxxxx0010011'],
    ['add', '0000000xxxxxxxxxx000xxxxx0110011'],
    ['sub', '0100000xxxxxxxxxx000xxxxx0110011'],
    ['sll', '0000000xxxxxxxxxx001xxxxx0110011'],
    ['slt', '0000000xxxxxxxxxx010xxxxx0110011'],
    ['sltu', '0000000xxxxxxxxxx011xxxxx0110011'],
    ['xor', '0000000xxxxxxxxxx100xxxxx0110011'],
    ['srl', '0000000xxxxxxxxxx101xxxxx0110011'],
    ['sra', '0100000xxxxxxxxxx101xxxxx0110011'],
    ['or', '0000000xxxxxxxxxx110xxxxx0110011'],
    ['and', '0000000xxxxxxxxxx111xxxxx0110011'],
    ['fence', 'xxxxxxxxxxxxxxxxx000xxxxx0001111'],
    ['fence_i', 'xxxxxxxxxxxxxxxxx001xxxxx0001111'],
    # ['scall', '00000000000000000000000001110011'],
    # ['sbreak', '00000000000100000000000001110011'],

]


# =======================================================================
# Instruction Definitions
# =======================================================================

def execute_lui(s, inst):
    s.rf[inst.rd] = inst.u_imm
    s.pc += 4


def disass_lui(inst):
    return "lui x{}, 0x{:x}".format(inst.rd, inst.u_imm)


def execute_auipc(s, inst):
    s.rf[inst.rd] = sext_xlen(inst.u_imm + s.pc)
    s.pc += 4


def disass_auipc(inst):
    return "auipc x{}, 0x{:x}".format(inst.rd, inst.u_imm)


def execute_jal(s, inst):
    tmp = sext_xlen(s.pc + 4)
    s.pc = JUMP_TARGET(s, inst)
    s.rf[inst.rd] = tmp


def disass_jal(inst):
    return "jal x{}, 0x{:x}".format(inst.rd, inst.uj_imm)


def execute_jalr(s, inst):
    tmp = sext_xlen(s.pc + 4)
    s.pc = (s.rf[inst.rs1] + inst.i_imm) & 0xFFFFFFFE
    s.rf[inst.rd] = tmp


def disass_jalr(inst):
    return "jalr x{}, 0x{:x}".format(inst.rd, inst.i_imm)


def execute_beq(s, inst):
    if s.rf[inst.rs1] == s.rf[inst.rs2]:
        s.pc = BRANCH_TARGET(s, inst)
    else:
        s.pc += 4


def disass_beq(inst):
    return "beq x{}, x{}, 0x{:x}".format(inst.rs1, inst.rs2, inst.sb_imm)


def execute_bne(s, inst):
    if s.rf[inst.rs1] != s.rf[inst.rs2]:
        s.pc = BRANCH_TARGET(s, inst)
    else:
        s.pc += 4


def disass_bne(inst):
    return "bne x{}, x{}, 0x{:x}".format(inst.rs1, inst.rs2, inst.sb_imm)


def execute_blt(s, inst):
    if signed(s.rf[inst.rs1], 64) < signed(s.rf[inst.rs2], 64):
        s.pc = BRANCH_TARGET(s, inst)
    else:
        s.pc += 4


def disass_blt(inst):
    return "blt x{}, x{}, 0x{:x}".format(inst.rs1, inst.rs2, inst.sb_imm)


def execute_bge(s, inst):
    if signed(s.rf[inst.rs1], 64) >= signed(s.rf[inst.rs2], 64):
        s.pc = BRANCH_TARGET(s, inst)
    else:
        s.pc += 4


def disass_bge(inst):
    return "bge x{}, x{}, 0x{:x}".format(inst.rs1, inst.rs2, inst.sb_imm)


def execute_bltu(s, inst):
    if s.rf[inst.rs1] < s.rf[inst.rs2]:
        s.pc = BRANCH_TARGET(s, inst)
    else:
        s.pc += 4


def disass_bltu(inst):
    return "bltu x{}, x{}, 0x{:x}".format(inst.rs1, inst.rs2, inst.sb_imm)


def execute_bgeu(s, inst):
    if s.rf[inst.rs1] >= s.rf[inst.rs2]:
        s.pc = BRANCH_TARGET(s, inst)
    else:
        s.pc += 4


def disass_bgeu(inst):
    return "bgeu x{}, x{}, 0x{:x}".format(inst.rs1, inst.rs2, inst.sb_imm)


def execute_lb(s, inst):
    addr = trim_64(s.rf[inst.rs1] + inst.i_imm)
    s.rf[inst.rd] = sext(s.mem.read(addr, 1), 8)
    s.pc += 4


def disass_lb(inst):
    return "lb x{}, x{}, 0x{:x}".format(inst.rd, inst.rs1, inst.i_imm)


def execute_lh(s, inst):
    addr = trim_64(s.rf[inst.rs1] + inst.i_imm)
    s.rf[inst.rd] = sext(s.mem.read(addr, 2), 16)
    s.pc += 4


def disass_lh(inst):
    return "lh x{}, x{}, 0x{:x}".format(inst.rd, inst.rs1, inst.i_imm)


def execute_lw(s, inst):
    addr = trim_64(s.rf[inst.rs1] + inst.i_imm)
    s.rf[inst.rd] = sext_32(s.mem.read(addr, 4))
    s.pc += 4


def disass_lw(inst):
    return "lw x{}, x{}, 0x{:x}".format(inst.rd, inst.rs1, inst.i_imm)


def execute_lbu(s, inst):
    addr = trim_64(s.rf[inst.rs1] + inst.i_imm)
    s.rf[inst.rd] = s.mem.read(addr, 1)
    s.pc += 4


def disass_lbu(inst):
    return "lbu x{}, x{}, 0x{:x}".format(inst.rd, inst.rs1, inst.i_imm)


def execute_lhu(s, inst):
    addr = trim_64(s.rf[inst.rs1] + inst.i_imm)
    s.rf[inst.rd] = s.mem.read(addr, 2)
    s.pc += 4


def disass_lhu(inst):
    return "lhu x{}, x{}, 0x{:x}".format(inst.rd, inst.rs1, inst.i_imm)


def execute_sb(s, inst):
    addr = trim_64(s.rf[inst.rs1] + inst.s_imm)
    s.mem.write(addr, 1, trim(s.rf[inst.rs2], 8))
    s.pc += 4


def disass_sb(inst):
    return "lb x{}, x{}, 0x{:x}".format(inst.rs2, inst.rs1, inst.s_imm)


def execute_sh(s, inst):
    addr = trim_64(s.rf[inst.rs1] + inst.s_imm)
    s.mem.write(addr, 2, trim(s.rf[inst.rs2], 16))
    s.pc += 4


def disass_sh(inst):
    return "sh x{}, x{}, 0x{:x}".format(inst.rs2, inst.rs1, inst.s_imm)


def execute_sw(s, inst):
    addr = trim_64(s.rf[inst.rs1] + inst.s_imm)
    s.mem.write(addr, 4, trim_32(s.rf[inst.rs2]))
    s.pc += 4


def disass_sw(inst):
    return "sw x{}, x{}, 0x{:x}".format(inst.rs2, inst.rs1, inst.s_imm)


def execute_addi(s, inst):
    s.rf[inst.rd] = sext_xlen(s.rf[inst.rs1] + inst.i_imm)
    s.pc += 4


def disass_addi(inst):
    return "addi x{}, x{}, 0x{:x}".format(inst.rd, inst.rs1, inst.i_imm)


def execute_slti(s, inst):
    s.rf[inst.rd] = signed(s.rf[inst.rs1], 64) < signed(inst.i_imm, 64)
    s.pc += 4


def disass_slti(inst):
    return "slti x{}, x{}, 0x{:x}".format(inst.rd, inst.rs1, inst.i_imm)


def execute_sltiu(s, inst):
    s.rf[inst.rd] = s.rf[inst.rs1] < inst.i_imm
    s.pc += 4


def disass_sltiu(inst):
    return "sltiu x{}, x{}, 0x{:x}".format(inst.rd, inst.rs1, inst.i_imm)


def execute_xori(s, inst):
    s.rf[inst.rd] = inst.i_imm ^ s.rf[inst.rs1]
    s.pc += 4


def disass_xori(inst):
    return "xori x{}, x{}, 0x{:x}".format(inst.rd, inst.rs1, inst.i_imm)


def execute_ori(s, inst):
    s.rf[inst.rd] = inst.i_imm | s.rf[inst.rs1]
    s.pc += 4


def disass_ori(inst):
    return "ori x{}, x{}, 0x{:x}".format(inst.rd, inst.rs1, inst.i_imm)


def execute_andi(s, inst):
    s.rf[inst.rd] = inst.i_imm & s.rf[inst.rs1]
    s.pc += 4


def disass_andi(inst):
    return "andi x{}, x{}, 0x{:x}".format(inst.rd, inst.rs1, inst.i_imm)


def execute_slli(s, inst):
    if SHAMT(s, inst) > s.xlen:
        raise TRAP_ILLEGAL_INSTRUCTION()
    s.rf[inst.rd] = sext_xlen(s.rf[inst.rs1] << SHAMT(s, inst))
    s.pc += 4


def disass_slli(inst):
    return "slii x{}, x{}, {}".format(inst.rd, inst.rs1, SHAMT(None, inst))


def execute_srli(s, inst):
    if s.xlen == 64:
        s.rf[inst.rd] = s.rf[inst.rs1] >> SHAMT(s, inst)
    elif SHAMT(s, inst) & 0x20:
        raise TRAP_ILLEGAL_INSTRUCTION()
    else:
        s.rf[inst.rd] = sext_32(s.rf[inst.rs1] >> SHAMT(s, inst))
    s.pc += 4


def disass_srli(inst):
    return "srli x{}, x{}, {}".format(inst.rd, inst.rs1, SHAMT(None, inst))


def execute_srai(s, inst):
    if s.xlen == 64:
        s.rf[inst.rd] = signed(s.rf[inst.rs1], 64) >> SHAMT(s, inst)
    elif SHAMT(s, inst) & 0x20:
        raise TRAP_ILLEGAL_INSTRUCTION()
    else:
        s.rf[inst.rd] = sext_32(s.rf[inst.rs1] >> SHAMT(s, inst))
    s.pc += 4


def disass_srai(inst):
    return "srai x{}, x{}, {}".format(inst.rd, inst.rs1, SHAMT(None, inst))


def execute_add(s, inst):
    s.rf[inst.rd] = sext_xlen(s.rf[inst.rs1] + s.rf[inst.rs2])
    s.pc += 4


def disass_add(inst):
    return "add x{}, x{}, x{}".format(inst.rd, inst.rs1, inst.rs2)


def execute_sub(s, inst):
    s.rf[inst.rd] = sext_xlen(s.rf[inst.rs1] - s.rf[inst.rs2])
    s.pc += 4


def disass_sub(inst):
    return "sub x{}, x{}, x{}".format(inst.rd, inst.rs1, inst.rs2)


def execute_sll(s, inst):
    shamt = s.rf[inst.rs2] & (s.xlen - 1)
    s.rf[inst.rd] = sext_xlen(s.rf[inst.rs1] << shamt)
    s.pc += 4


def disass_sll(inst):
    return "sll x{}, x{}, x{}".format(inst.rd, inst.rs1, inst.rs2)



def execute_slt(s, inst):
    s.rf[inst.rd] = signed(s.rf[inst.rs1], 64) < signed(s.rf[inst.rs2], 64)
    s.pc += 4


def disass_slt(inst):
    return "slt x{}, x{}, x{}".format(inst.rd, inst.rs1, inst.rs2)


def execute_sltu(s, inst):
    s.rf[inst.rd] = s.rf[inst.rs1] < s.rf[inst.rs2]
    s.pc += 4


def disass_sltu(inst):
    return "sltu x{}, x{}, x{}".format(inst.rd, inst.rs1, inst.rs2)


def execute_xor(s, inst):
    s.rf[inst.rd] = s.rf[inst.rs1] ^ s.rf[inst.rs2]
    s.pc += 4


def disass_xor(inst):
    return "xor x{}, x{}, x{}".format(inst.rd, inst.rs1, inst.rs2)


def execute_srl(s, inst):
    if s.xlen == 64:
        s.rf[inst.rd] = s.rf[inst.rs1] >> (s.rf[inst.rs2] & 0x3F)
    else:
        s.rf[inst.rd] = sext_32(s.rf[inst.rs1] >> (s.rf[inst.rs2] & 0x1F))
    s.pc += 4


def disass_srl(inst):
    return "srl x{}, x{}, x{}".format(inst.rd, inst.rs1, inst.rs2)


def execute_sra(s, inst):
    s.rf[inst.rd] = sext_xlen(
        signed(s.rf[inst.rs1], 64) >> (s.rf[inst.rs2] & (s.xlen - 1))
    )
    s.pc += 4


def disass_sra(inst):
    return "sra x{}, x{}, x{}".format(inst.rd, inst.rs1, inst.rs2)


def execute_or(s, inst):
    s.rf[inst.rd] = s.rf[inst.rs1] | s.rf[inst.rs2]
    s.pc += 4


def disass_or(inst):
    return "or x{}, x{}, x{}".format(inst.rd, inst.rs1, inst.rs2)


def execute_and(s, inst):
    s.rf[inst.rd] = s.rf[inst.rs1] & s.rf[inst.rs2]
    s.pc += 4


def disass_and(inst):
    return "sra x{}, x{}, x{}".format(inst.rd, inst.rs1, inst.rs2)


def execute_fence(s, inst):
    s.pc += 4


def execute_fence_i(s, inst):
    # TODO: MMU flush icache
    s.pc += 4

