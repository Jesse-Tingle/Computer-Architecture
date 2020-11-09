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
        else:
            raise Exception("Unsupported ALU operation")

    def trace(self):
        """
        Handy function to print out the CPU state. You might want to call this
        from run() if you need help debugging.
        """

        print(
            f"TRACE: %02X | %02X %02X %02X |"
            % (
                self.pc,

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
        operand_a = self.ram[self.pc + 1]
        operand_b = self.ram[self.pc + 2]
        self.alu("MUL", operand_a, operand_b)
        self.pc += 3

    def add(self):
        operand_a = self.ram[self.pc + 1]
        operand_b = self.ram[self.pc + 2]
        self.alu("ADD", operand_a, operand_b)
        self.pc += 3

    def ldi(self):
        operand_a = self.ram[self.pc + 1]
        operand_b = self.ram[self.pc + 2]
        self.reg[operand_a] = operand_b
        self.pc += 3

    def hlt(self):
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
