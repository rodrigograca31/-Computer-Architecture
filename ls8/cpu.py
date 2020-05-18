"""CPU functionality."""

import sys
import re


class CPU:
    """Main CPU class."""

    def __init__(self):
        """Construct a new CPU."""
        self.running = False
        self.pc = 0
        self.reg = [0] * 8
        self.ram = [0] * 256
        pass

    def load(self, args):
        """Load a program into memory."""

        address = 0
        if(len(args) == 2):
            with open(args[1], "r") as file:
                for instruction in file:
                    instruction = re.sub(
                        r'[^01]+', '', instruction.split("#")[0])
                    # print(re.sub(r'[^01]+', '', instruction.split("#")[0]))
                    if instruction != "":
                        # self.ram[address] = bin(int("0b"+instruction, 2))
                        self.ram_write(address, int(instruction, 2))
                        address += 1

        # For now, we've just hardcoded a program:

        # program = [
        #     # From print8.ls8
        #     0b10000010,  # LDI R0,8
        #     0b00000000,
        #     0b00001000,
        #     0b01000111,  # PRN R0
        #     0b00000000,
        #     0b00000001,  # HLT
        # ]

        # for instruction in program:
        #     self.ram[address] = instruction
        #     address += 1

    def alu(self, op, reg_a, reg_b):
        """ALU operations."""

        # print("Operation: ", op)
        if op == "LDI":
            self.reg[reg_a] = reg_b

        elif op == "ADD":
            self.reg[reg_a] += self.reg[reg_b]
        elif op == "SUB":
            self.reg[reg_a] -= self.reg[reg_b]
        elif op == "MUL":
            self.reg[reg_a] *= self.reg[reg_b]
        elif op == "DIV":
            self.reg[reg_a] /= self.reg[reg_b]
        elif op == "MOD":
            self.reg[reg_a] %= self.reg[reg_b]

        elif op == "PRN":
            print(self.reg[reg_a])
        elif op == "HLT":
            exit()
        else:
            raise Exception("Unsupported ALU operation")

    def trace(self):
        """
        Handy function to print out the CPU state. You might want to call this
        from run() if you need help debugging.
        """

        print(f"TRACE: %02X | %02X %02X %02X |" % (
            self.pc,
            # self.fl,
            # self.ie,
            self.ram_read(self.pc),
            self.ram_read(self.pc + 1),
            self.ram_read(self.pc + 2)
        ), end='')

        for i in range(8):
            print(" %02X" % self.reg[i], end='')

        print()

    def ram_read(self, pc=None):
        if pc == None:
            pc = self.pc
        # self.pc += 1
        return self.ram[pc]

    def ram_write(self, pc, value):
        self.ram[pc] = value

    def run(self):
        """Run the CPU."""
        self.running = True
        op_size = 0

        while self.running:
            # print("read:", self.pc)
            IR = self.ram_read(self.pc)  # Instruction Register
            # print(f"read:{IR:b}")
            operand_a = self.ram_read(self.pc + 1)
            operand_b = self.ram_read(self.pc + 2)

            if IR == 0:
                exit()
            elif IR == 0b10000010:  # LDI load "immediate"
                self.alu("LDI", operand_a, operand_b)
                op_size = 3
            elif IR == 0b10100000:
                self.alu("ADD", operand_a, operand_b)
                op_size = 3
            elif IR == 0b10100001:
                self.alu("SUB", operand_a, operand_b)
                op_size = 3
            elif IR == 0b10100010:
                self.alu("MUL", operand_a, operand_b)
                op_size = 3
            elif IR == 0b10100011:
                self.alu("DIV", operand_a, operand_b)
                op_size = 3
            elif IR == 0b10100100:
                self.alu("MOD", operand_a, operand_b)
                op_size = 3

            elif IR == 0b01000111:
                self.alu("PRN", operand_a, operand_b)
                op_size = 2

            elif IR == 0b00000001:
                self.alu("HLT", operand_a, operand_b)
                op_size = 1

            else:
                print(f"invalid instruction [{self.ram[self.pc]:b}]")
                running = False
                op_size = 1

            self.pc += op_size
