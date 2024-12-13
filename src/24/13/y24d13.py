# Path: /home/g/Code/advent-of-python/src/24/13/y24d13.py
# Puzzle Source: https://adventofcode.com/2024/day/13
from dataclasses import dataclass, field
from typing import TypeVar


def load_txt_lines(named: str):
    from pathlib import Path
    with Path(__file__).parent.joinpath(f'{named}.txt').open('r') as f:
        lines = f.read().split('\n')
    return lines[:-1] if len(lines[-1]) == 0 else lines


@dataclass
class Point:
    x: int
    y: int

    def __hash__(self):
        return hash((self.x, self.y))

    def __add__(self, other):
        return Point(self.x + other.x, self.y + other.y)

    def __sub__(self, other):
        return Point(self.x - other.x, self.y - other.y)

    def __mul__(self, other):
        return Point(self.x * other, self.y * other)

    def dot(self, other):
        return self.x * other.x + self.y * other.y

    def __str__(self):
        return f'({self.x}, {self.y})'


@dataclass
class ClawMachine:
    a: Point
    b: Point
    goal: Point

    def solve(self, offset: int):
        det = self.a.x * self.b.y - self.b.x * self.a.y
        g = self.goal + Point(offset, offset)
        a = (g.x * self.b.y - g.y * self.b.x) // det
        b = (g.y * self.a.x - g.x * self.a.y) // det
        if self.a * a + self.b * b == g:
            return Point(a, b)
        return Point(0, 0)

    def cost(self, a: int, b: int, offset: int):
        return Point(a, b).dot(self.solve(offset))

    @classmethod
    def from_lines(cls, lines: list[str]):
        assert len(lines) == 3
        import re
        r = re.compile(r'X(?:\+|=)(?P<x>[0-9]*), Y(?:\+|=)(?P<y>[0-9]*)')
        points = [Point(int(g['x']), int(g['y'])) for line in lines for g in (r.search(line).groupdict(), )]
        return cls(*points)


@dataclass
class Arcade:
    machines: list[ClawMachine]

    @classmethod
    def from_lines(cls, lines: list[str]):
        lines = [line for line in lines if len(line)]
        machines = [ClawMachine.from_lines(lines[3*n:3*n+3]) for n in range(len(lines)//3)]
        return cls(machines)

    def cost(self, offset=0):
        return sum(m.cost(3, 1, offset) for m in self.machines)



def part1(lines: list[str]) -> int:
    return Arcade.from_lines(lines).cost()


def part2(lines: list[str]) -> int:
    return Arcade.from_lines(lines).cost(offset = 10000000000000)


if __name__ == '__main__':
    from faoci.interface import fetch_lines
    assert part1(load_txt_lines('example')) == 480
    print(f'Part 1: {part1(fetch_lines(year=2024, day=13))}')
    print(f'Part 2: {part2(fetch_lines(year=2024, day=13))}')
