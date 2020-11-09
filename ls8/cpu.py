"""CPU functionality."""

import sys

HLT = 0b00000001
LDI = 0b10000010
PRN = 0b01000111
MUL = 0b10100010
PUSH = 0b01000101
POP = 0b01000110
CALL = 0b01010000
RET = 0b00010001
ADD = 0b10100000

# sprint

L_MASK = 0b00000100
G_MASK = 0b00000010
E_MASK = 0b00000001
# instructions
CMP = 0b10100111
JMP = 0b01010100
JNE = 0b01010110
JEQ = 0b01010101

# stretch problems
AND = 0b10101000
OR = 0b10101010
NOT = 0b01101001
XOR = 0b10101011
SHL = 0b10101100
SHR = 0b10101101
MOD = 0b10100100


class CPU:
    """Main CPU class."""

    def __init__(self):
        """Construct a new CPU."""
        self.ram = [0] * 256
        self.reg = [0] * 8
        # stack pointer
        self.sp = 7
        self.pc = 0
        self.running = False
        self.branchtable = {}
        self.branchtable[HLT] = self.hlt
        self.branchtable[LDI] = self.ldi
        self.branchtable[PRN] = self.prn
        self.branchtable[MUL] = self.mul
        self.branchtable[PUSH] = self.push
        self.branchtable[POP] = self.pop
        self.branchtable[CALL] = self.call
        self.branchtable[RET] = self.ret
        self.branchtable[ADD] = self.add
        # sprint
        self.branchtable[CMP] = self.cmp
        self.branchtable[JMP] = self.jmp
        self.branchtable[JNE] = self.jne
        self.branchtable[JEQ] = self.jeq
        # flag
        self.flag = 0

        # stretch goal
        self.branchtable[AND] = self.and_func
        self.branchtable[OR] = self.or_func
        self.branchtable[NOT] = self.not_func
        self.branchtable[XOR] = self.xor
        # self.branchtable[SHL] = self.shl
        # self.branchtable[SHR] = self.shr
        # self.branchtable[MOD] = self.mod

    def ram_read(self, MAR):
        return self.ram[MAR]

    def ram_write(self, MAR, MDR):
        self.ram[MAR] = MDR

    def load(self):
        """Load a program into memory."""

        address = 0

        try:
            with open(sys.argv[1]) as f:
                for line in f:
                    try:
                        line = line.strip().split("#", 1)[0]
                        line = int(line, 2)
                        self.ram[address] = line
                        address += 1
                    except ValueError:
                        pass
        except FileNotFoundError:
            print(f"Couldn't find file {sys.argv[1]}")
            sys.exit(1)
        except IndexError:
            print("Usage: ls8.py filename")
            sys.exit(1)

    def alu(self, op, reg_a, reg_b):
        """ALU operations."""

        if op == "ADD":
            self.reg[reg_a] += self.reg[reg_b]
        elif op == "MUL":
            self.reg[reg_a] *= self.reg[reg_b]

        elif op == "CMP":
            if self.reg[reg_a] < self.reg[reg_b]:
                self.flag = L_MASK
            elif self.reg[reg_a] > self.reg[reg_b]:
                self.flag = G_MASK
            else:
                self.flag = E_MASK
        # STRETCH
        elif op == "AND":
            self.reg[reg_a] = self.reg[reg_a] & self.reg[reg_b]
        elif op == "OR":
            self.reg[reg_a] = self.reg[reg_a] | self.reg[reg_b]
        elif op == "NOT":
            self.reg[reg_a] = ~self.reg[reg_a]
            self.reg[reg_b] = ~self.reg[reg_b]
        elif op == "XOR":
            self.reg[reg_a] = self.reg[reg_a] ^ self.reg[reg_b]
        elif op == "SHL":
            self.reg[reg_a] << self.reg[reg_b]
        elif op == "SHR":
            self.reg[reg_a] >> self.reg[reg_b]
        elif op == "MOD":
            if self.reg[reg_b] == 0:
                print("Error, second value is 0")
                self.pc = HLT
            else:
                remainder = self.reg[reg_a] % self.reg[reg_b]
                self.reg[reg_a] = remainder
        else:
            raise Exception("Unsupported ALU operation")

    def operation_helper(self, op):
        operand_a = self.ram[self.pc + 1]
        operand_b = self.ram[self.pc + 2]
        self.alu(op, operand_a, operand_b)
        self.pc += 3

    # STRETCH - AND` `OR` `XOR` `NOT` `SHL` `SHR` `MOD`
    def and_func(self):
        self.operation_helper("AND")

    def or_func(self):
        self.operation_helper("OR")

    def not_func(self):
        self.operation_helper("NOT")

    def xor(self):
        self.operation_helper("XOR")

    def shl(self):
        self.operation_helper("SHL")

    def shr(self):
        self.operation_helper("SHR")

    def mod(self):
        self.operation_helper("MOD")

    def trace(self):
        """
        Handy function to print out the CPU state. You might want to call this
        from run() if you need help debugging.
        """

        print(
            f"TRACE: %02X | %02X %02X %02X |"
            % (
                self.pc,
                # self.fl,
                # self.ie,
                self.ram_read(self.pc),
                self.ram_read(self.pc + 1),
                self.ram_read(self.pc + 2),
            ),
            end="",
        )

        for i in range(8):
            print(" %02X" % self.reg[i], end="")

        print()

    def mul(self):
        self.operation_helper("MUL")

    def add(self):
        self.operation_helper("ADD")

    def ldi(self):
        operand_a = self.ram[self.pc + 1]
        operand_b = self.ram[self.pc + 2]
        self.reg[operand_a] = operand_b
        self.pc += 3

    def hlt(self):
        # stops the program
        self.running = False

    def prn(self):
        operand_a = self.ram[self.pc + 1]
        print(self.reg[operand_a])
        self.pc += 2

    def push(self):
        self.reg[self.sp] -= 1
        reg_num = self.ram[self.pc + 1]
        value = self.reg[reg_num]

        self.ram[self.reg[self.sp]] = value

        self.pc += 2

    def pop(self):
        reg_num = self.ram[self.pc + 1]
        value = self.ram[self.reg[self.sp]]
        self.reg[reg_num] = value
        self.reg[self.sp] += 1
        self.pc += 2

    def call(self):
        ret_addr = self.pc + 2
        self.reg[self.sp] -= 1
        self.ram[self.reg[self.sp]] = ret_addr

        reg_num = self.ram[self.pc + 1]
        self.pc = self.reg[reg_num]

    def ret(self):
        ret_addr = self.ram[self.reg[self.sp]]
        self.reg[self.sp] += 1
        self.pc = ret_addr

    def cmp(self):
        operand_a = self.ram[self.pc + 1]
        operand_b = self.ram[self.pc + 2]
        self.alu("CMP", operand_a, operand_b)
        self.pc += 3

    def jmp(self):
        self.pc += 1
        given_reg = self.ram[self.pc]
        self.pc = self.reg[given_reg]

    def jeq(self):
        given_reg = self.ram[self.pc + 1]
        if self.flag == E_MASK:
            self.pc = self.reg[given_reg]
        else:
            self.pc += 2

    def jne(self):
        given_reg = self.ram[self.pc + 1]
        if self.flag != E_MASK:
            self.pc = self.reg[given_reg]
        else:
            self.pc += 2

    def run(self):
        """Run the CPU."""
        self.running = True
        while self.running:
            ir = self.pc
            inst = self.ram[ir]
            try:
                self.branchtable[inst]()
            except KeyError:
                print(f"KeyError at {self.reg[self.ram[inst]]}")
                sys.exit(1)
