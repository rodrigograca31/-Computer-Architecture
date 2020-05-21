"""CPU functionality."""

import sys
import re


class CPU:
    """Main CPU class."""

    def __init__(self):
        """Construct a new CPU."""
        self.running = False    # Self explanatory
        self.PC = 0             # Program Counter, address of the currently executing instruction
        self.reg = [0] * 8      # Registers, R0-R7, to hold values
        # Register 7 is the Stack Pointer (index of register that knows where the stack is at) self.reg[sp] += 1
        self.sp = 7
        # self.ram[self.reg[self.sp]] = 244 - Is the top of the stack and grows down
        self.reg[self.sp] = 0xF4
        self.ram = [0] * 256    # RAM to load the program into.
        self.branchtable = {    # branchtable avoids if/elif statements by using an index to know which function to run
            0b10000010: self.LDI,   # Load "Immediate"
            0b10100000: self.ADD,   # ALU function
            0b10100001: self.SUB,   # ALU function
            0b10100010: self.MUL,   # ALU function
            0b10100011: self.DIV,   # ALU function
            0b10100100: self.MOD,   # ALU function
            0b01000111: self.PRN,   # Print
            0b00000001: self.HLT,   # Halt
            0b01000101: self.PUSH,  # Push
            0b01000110: self.POP,   # Pop
            0b01010000: self.CALL,  # Call
            0b00010001: self.RET    # Return to
        }

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

    def alu(self, op, reg_a, reg_b):
        """ALU (Arithmetic Logic Instructions) operations."""

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
            self.PC,
            # self.fl,
            # self.ie,
            self.ram_read(self.PC),
            self.ram_read(self.PC + 1),
            self.ram_read(self.PC + 2)
        ), end='')

        for i in range(8):
            print(" %02X" % self.reg[i], end='')

        print()

    def ram_read(self, position):
        return self.ram[position]

    def ram_write(self, position, value):
        self.ram[position] = value

    def LDI(self, position, value):
        """Load Immediate"""
        self.reg[position] = value

    def ADD(self, a, b):
        self.alu("ADD", a, b)

    def SUB(self, a, b):
        self.alu("SUB", a, b)

    def MUL(self, a, b):
        self.alu("MUL", a, b)

    def DIV(self, a, b):
        self.alu("DIV", a, b)

    def MOD(self, a, b):
        self.alu("MOD", a, b)

    def PRN(self, position):
        print(self.reg[position])

    def HLT(self):
        self.running = False  # This is not really needed
        sys.exit(0)

    # pushes a given register to the stack
    def PUSH(self, register):
        self.reg[self.sp] -= 1
        self.ram_write(self.reg[self.sp], self.reg[register])

    # pops from the stack into a given register
    def POP(self, register):
        self.reg[register] = self.ram_read()[self.reg[self.sp]]
        self.reg[self.sp] += 1

    def CALL(self, register):
        """
        Saves the next instruction address in the stack to later return to
        and sets the PC (Program Counter) to a given register value that stored where it wants to go/call
        """

        self.reg[self.sp] -= 1
        # plus 2 because its the current instruction + the next one + the actual one it should come to later when it does RET
        self.ram_write(self.reg[self.sp], self.PC + 2)
        # minus two because this the operation size (op_size) is 1 and +1 after
        self.PC = self.reg[register] - 2

    def RET(self):
        """
        Pops the next instruction address from the stack (the one that stored before it went somewhere)
        and sets the PC (Program Counter) to it so that it returns to a given instruction
        """

        # minus 1 because this the operation size (op_size) does +1 after
        self.PC = self.ram_read(self.reg[self.sp]) - 1
        self.reg[self.sp] += 1

    def run(self):
        """Run the CPU."""

        self.running = True
        op_size = 0  # operation size

        while self.running:
            IR = self.ram_read(self.PC)  # Instruction Register

            """
            This does a bitwise operation to shift the current IR (Instruction Register) value by 6 bits in this >> direction
            so that 0b10000010 turns into 0b00000010
            and 0b01000010 turns into 0b00000001
            (ads 6 zeros on the left side, pushing everything else right and "eliminating/clipping it")
            that tells us how many "jumps" we have to increase by (0, 1 or 2)
            In other words: it turns the 2 "highest" (left) bits into a new binary 00, 01, 10 
            that tells us how many operants will follow the current instruction, 0, 1, 2
            """
            op_size = (IR >> 6)

            operand_a = self.ram_read(self.PC + 1)
            operand_b = self.ram_read(self.PC + 2)

            # print(f"{IR:08b}")
            # print(f"{self.branchtable[IR]}")

            try:
                if op_size == 0:
                    self.branchtable[IR]()
                elif op_size == 1:
                    self.branchtable[IR](operand_a)
                elif op_size == 2:
                    self.branchtable[IR](operand_a, operand_b)
            except KeyError:
                print(f"invalid instruction [{self.ram[self.PC]:08b}]")
                running = False

            self.PC += (op_size+1)
