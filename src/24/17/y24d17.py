# Path: /home/g/Code/advent-of-python/src/24/17/y24d17.py
# Puzzle Source: https://adventofcode.com/2024/day/17
from dataclasses import dataclass, field

def get_lines(filename):
    from pathlib import Path
    if isinstance(filename, str):
        filename = Path(filename)
    filename = filename.resolve()
    if not filename.exists():
        return []

    with open(filename, 'r') as file:
        return file.read().splitlines()


@dataclass
class Computer:
    a: int = 0
    b: int = 0
    c: int = 0
    instructions: list[int] = field(default_factory=list)
    pointer: int = 0
    stdout: list[int] = field(default_factory=list)

    @classmethod
    def from_lines(cls, lines: list[str]):
        a, b, c = [int(line.split(':')[-1]) for line in lines[:3]]
        instructions = [int(x) for x in lines[-1].split(':')[-1].split(',')]
        return cls(a, b, c, instructions)

    def combo(self, operand: int):
        if 0 <= operand < 4:
            return operand
        if 4 == operand:
            return self.a
        if 5 == operand:
            return self.b
        if 6 == operand:
            return self.c
        raise ValueError(f'Invalid combo operand {operand}')

    def adv(self, combo_operand: int):
        self.a //= 2 ** combo_operand
        self.pointer += 2
        return self

    def bxl(self, literal_operand: int):
        self.b ^= literal_operand
        self.pointer += 2
        return self

    def bst(self, combo_operand: int):
        self.b = combo_operand % 8
        self.pointer += 2
        return self

    def jnz(self, literal_operand: int):
        self.pointer = literal_operand if self.a else self.pointer + 2
        return self

    def bxc(self):
        return self.bxl(self.c)

    def out(self, combo_operand: int):
        self.stdout.append(combo_operand % 8)
        self.pointer += 2
        return self

    def bdv(self, combo_operand: int):
        self.b = self.a // 2 ** combo_operand
        self.pointer += 2
        return self

    def cdv(self, combo_operand: int):
        self.c = self.a // 2 ** combo_operand
        self.pointer += 2
        return self

    def operate(self, opcode: int, operand: int):
        if 0 == opcode:
            return self.adv(self.combo(operand))
        if 1 == opcode:
            return self.bxl(operand)
        if 2 == opcode:
            return self.bst(self.combo(operand))
        if 3 == opcode:
            return self.jnz(operand)
        if 4 == opcode:
            return self.bxc()
        if 5 == opcode:
            return self.out(self.combo(operand))
        if 6 == opcode:
            return self.bdv(self.combo(operand))
        if 7 == opcode:
            return self.cdv(self.combo(operand))
        raise RuntimeError(f'Invalid opcode {opcode}')

    def run(self, a: int | None = None, b: int | None = None, c: int | None = None):
        if a:
            self.a = a
        if b:
            self.b = b
        if c:
            self.c = c
        self.pointer = 0
        self.stdout = []
        while self.pointer + 1 < len(self.instructions):
            opcode, operand = self.instructions[self.pointer], self.instructions[self.pointer+1]
            self.operate(opcode, operand)
        return self.stdout


def part1(lines: list[str]) -> int:
    comp = Computer.from_lines(lines)
    return comp.run()


def part2(lines: list[str]) -> int:
    from math import log, floor

    comp = Computer.from_lines(lines)
    a, b, c = 8**(len(comp.instructions)-1), comp.b, comp.c
    out = comp.run(a, b, c)
    while len(out) == len(comp.instructions) and out != comp.instructions and a < (8 ** len(comp.instructions)):
        n = int(floor(log(a, 8)))
        for i in range(n):
            if out[-1-i] == comp.instructions[-1-i]:
                n -= 1
            else:
                break
        a += 8**n
        out = comp.run(a, b, c)
    return a


if __name__ == '__main__':
    from faoci.interface import fetch_lines

    assert part1(get_lines('y24d17.test')) == [4,6,3,5,6,3,5,2,1,0]
    assert part2(get_lines('y24d17.b.test')) == 117440

    puzzle = fetch_lines(year=2024, day=17)
    p1 = ','.join(str(x) for x in part1(puzzle))
    print(f'Part 1: {p1}')
    print(f'Part 2: {part2(puzzle)}')
