"""CPU functionality."""

import sys
import re


class CPU:
    """Main CPU class."""

    def __init__(self):
        """Construct a new CPU."""
        self.running = False    # Self explanatory
        self.pc = 0             # Program Counter, address of the currently executing instruction
        self.reg = [0] * 8      # Registers, R0-R8, to hold values
        self.ram = [0] * 256    # RAM to load the program into.
        pass

    def load(self, args):
        """Load a program into memory."""

        address = 0
        if(len(args) == 2):
            try:
                with open(args[1], "r") as file:
                    for instruction in file:
                        instruction = re.sub(
                            r'[^01]+', '', instruction.split("#")[0])
                        # print(re.sub(r'[^01]+', '', instruction.split("#")[0]))
                        if instruction != "":
                            # self.ram[address] = bin(int("0b"+instruction, 2))
                            # print(f"{int(instruction,2):08b}")
                            self.ram_write(address, int(instruction, 2))
                            address += 1
            except FileNotFoundError:
                print("file not found!")
                sys.exit(2)
        else:
            print("usage: ./ls8.py <filename>")
            sys.exit(1)

        # print(self.ram)

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

    '''
    Arithmetic Logic Instructions
    '''

    def alu(self, op, reg_a, reg_b):
        """ALU operations."""

        # print("Operation: ", op)
        if op == "ADD":
            self.reg[reg_a] += self.reg[reg_b]
        elif op == "SUB":
            self.reg[reg_a] -= self.reg[reg_b]
        elif op == "MUL":
            self.reg[reg_a] *= self.reg[reg_b]
        elif op == "DIV":
            self.reg[reg_a] /= self.reg[reg_b]
        elif op == "MOD":
            self.reg[reg_a] %= self.reg[reg_b]
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
        op_size = 0  # operation size

        while self.running:
            # print("read:", self.pc)
            IR = self.ram_read(self.pc)  # Instruction Register
            # print(f"read:{IR:b}")
            operand_a = self.ram_read(self.pc + 1)
            operand_b = self.ram_read(self.pc + 2)

            if IR == 0:
                sys.exit(0)
            elif IR == 0b10000010:  # LDI load "immediate"
                # shift by 6 to know how many to read. like in morning repo
                self.reg[operand_a] = operand_b
                # does a bitwise operation to shift the current IR (Instruction Register) value by 6 bits
                # so that 0b10000010 turns into 0b00000010
                # and 0b01000010 turns into 0b00000001
                # that tells us how many instructions we have to increase by (1 or 2)
                op_size = (IR >> 6) + 1
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
                print(self.reg[operand_a])
                op_size = 2
            elif IR == 0b00000001:
                sys.exit(0)
                op_size = 1
                # running = False
            else:
                print(f"invalid instruction [{self.ram[self.pc]:b}]")
                running = False
                op_size = 1

            self.pc += op_size
