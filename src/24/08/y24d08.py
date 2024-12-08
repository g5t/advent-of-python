# Path: /home/g/Code/advent-of-python/src/24/08/y24d08.py
# Puzzle Source: https://adventofcode.com/2024/day/8
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

    def __str__(self):
        return f'({self.x}, {self.y})'


@dataclass
class A:
    name: str
    at: tuple[Point, ...] = field(default_factory=tuple)

    def pairs(self):
        from itertools import permutations
        return permutations(self.at, 2)

    def antinodes_at(self, a: Point, b: Point, xmax: int, ymax: int):
        d = a - b
        return [p for p in (a + d, b - d) if 0 <= p.x <= xmax and 0 <= p.y <= ymax]

    def resonant_at(self, a: Point, b: Point, xmax: int, ymax: int):
        d = a - b
        n_max = max(xmax // abs(d.x) if d.x else 0, ymax // abs(d.y) if d.y else 0) + 1
        return [p for p in [b + d * n for n in range(-n_max, n_max + 1)] if 0 <= p.x <= xmax and 0 <= p.y <= ymax]

    def antinodes(self, xmax: int, ymax:int, resonant=False):
        an = set()
        for a, b in self.pairs():
            for p in (self.resonant_at if resonant else self.antinodes_at)(a, b, xmax, ymax):
                an.add(p)
        return an


@dataclass
class M:
    x_max: int
    y_max: int
    frequencies: tuple[A,...]

    def antinodes(self, resonant=False):
        an = set()
        for freq in self.frequencies:
            an = an.union(freq.antinodes(self.x_max, self.y_max, resonant=resonant))
        return an

    def to_str(self, nodes=None, freq=True):
        m = [['.' for _ in range(self.x_max+1)] for _ in range(self.y_max+1)]
        if nodes:
            for node in nodes:
                m[node.y][node.x] = '#'
        if freq:
            for freq in self.frequencies:
                for at in freq.at:
                    m[at.y][at.x] = freq.name[0]
        return '\n'.join(''.join(c for c in line) for line in m)

    @classmethod
    def from_lines(cls, lines: list[str]):
        from itertools import product
        y_size, x_size = len(lines), len(lines[0])
        assert all(len(l) == x_size for l in lines)
        fs = {}
        for x, y in product(range(x_size), range(y_size)):
            if (c:=lines[y][x]) != '.':
                fs[c] = fs.get(c, tuple()) + (Point(x, y),)

        return cls(x_size - 1, y_size - 1, tuple(A(k, v) for k, v in fs.items()))


def part1(lines: list[str]) -> int:
    return len(M.from_lines(lines).antinodes())


def part2(lines: list[str]) -> int:
    return len(M.from_lines(lines).antinodes(resonant=True))


if __name__ == '__main__':
    from faoci.interface import fetch_lines

    assert part1(load_txt_lines('example')) == 14
    assert part2(load_txt_lines('example')) == 34

    print(f'Part 1: {part1(fetch_lines(year=2024, day=8))}')
    print(f'Part 2: {part2(fetch_lines(year=2024, day=8))}')
