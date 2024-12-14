# Path: /home/g/Code/advent-of-python/src/24/14/y24d14.py
# Puzzle Source: https://adventofcode.com/2024/day/14
from dataclasses import dataclass, field
from typing import TypeVar


@dataclass
class Point:
    x: int
    y: int

    def __hash__(self):
        return hash((self.x, self.y))

    def __add__(self, other):
        if isinstance(other, Point):
            return Point(self.x + other.x, self.y + other.y)
        return Point(self.x + other, self.y + other)

    def __sub__(self, other):
        if isinstance(other, Point):
            return Point(self.x - other.x, self.y - other.y)
        return Point(self.x - other, self.y - other)

    def __mul__(self, other):
        if isinstance(other, Point):
            return self.x * other.x + self.y * other.y
        return Point(self.x * other, self.y * other)
    
    def __floordiv__(self, other):
        if isinstance(other, Point):
            return Point(self.x // other.x, self.y // other.y)
        return Point(self.x // other, self.y // other)

    def __rmul__(self, other):
        return Point(other * self.x, other * self.y)

    def __mod__(self, other):
        if isinstance(other, Point):
            return Point(self.x % other.x, self.y % other.y)
        return Point(self.x % other, self.y % other)

    def __str__(self):
        return f'({self.x}, {self.y})'

    @classmethod
    def from_str(cls, s: str):
        return cls(*[int(x) for x in s.split(',')])


@dataclass
class Robot:
    p: Point
    v: Point

    @classmethod
    def from_line(cls, line: str):
        p, v= [Point.from_str(l_s.split('=')[-1]) for l_s in line.split()]
        return cls(p, v)

    def position_at(self, time: int, size: Point) -> Point:
        return (self.p + time * self.v) % size


@dataclass
class Space:
    size: Point
    robots: tuple[Robot,...]

    @classmethod
    def from_lines(cls, size: Point, lines: list[str]):
        return cls(size, tuple(Robot.from_line(line) for line in lines))

    def quadrant_counts(self) -> tuple[int, int, int, int]:
        nw, ne, se, sw = 0, 0, 0, 0
        midpoint = self.size - self.size // 2 - Point(1,1) # 0-indexing offset
        for r in self.robots:
            p = r.p
            if p.x == midpoint.x or p.y == midpoint.y:
                continue
            if p.x < midpoint.x:
                if p.y < midpoint.y:
                    nw += 1
                else:
                    sw += 1
            else:
                if p.y < midpoint.y:
                    ne += 1
                else:
                    se += 1
        return nw, ne, se, sw


    def safety_factor(self) -> int:
        nw, ne, se, sw = self.quadrant_counts()
        return nw * ne * se * sw

    def has_line(self, f: Point, d: Point, n: int):
        if n <= 0:
            return True
        if any(r.p == f + d for r in self.robots):
            return self.has_line(f + d, d, n-1)
        return False

    def tree_candidate(self) -> bool:
        for b in self.robots:
            if any(b.p == r.p and b != r for r in self.robots):
                return False
        in_a_row = 4
        d = Point(0, 1)
        for b in self.robots:
            if self.has_line(b.p, d, in_a_row):
                return True
        return False

    def after(self, time: int):
        r = tuple(Robot(x.position_at(time, self.size), x.v) for x in self.robots)
        return Space(self.size, r)

    def __str__(self):
        n = [[0 for _ in range(self.size.x)] for _ in range(self.size.y)]
        for r in self.robots:
            n[r.p.y][r.p.x] += 1
        return '\n'.join(''.join(hex(v)[-1] if v else '.' for v in row) for row in  n)


def get_lines(filename):
    from pathlib import Path
    if isinstance(filename, str):
        filename = Path(filename)
    filename = filename.resolve()
    if not filename.exists():
        return []

    with open(filename, 'r') as file:
        return file.read().splitlines()


def part1(lines: list[str], size: Point | None = None) -> int:
    if size is None:
        size = Point(101, 103)
    space = Space.from_lines(size, lines)
    s100 = space.after(100)
    return s100.safety_factor()


def part2(lines: list[str]) -> int:
    size = Point(101, 103)
    space = Space.from_lines(size, lines)
    steps = 0
    while True:
        if space.tree_candidate():
            print(space)
            return steps
        steps += 1
        space = space.after(1)


if __name__ == '__main__':
    from faoci.interface import fetch_lines

    assert part1(get_lines('y24d14.test'), size=Point(11, 7)) == 12

    puzzle = fetch_lines(year=2024, day=14)
    print(f'Part 1: {part1(puzzle)}')
    print(f'Part 2: {part2(puzzle)}')
