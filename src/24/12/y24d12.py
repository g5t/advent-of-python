# Path: /home/g/Code/advent-of-python/src/24/12/y24d12.py
# Puzzle Source: https://adventofcode.com/2024/day/12
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
class Region:
    name: chr
    points: set[Point]

    @property
    def area(self):
        return len(self.points)

    @property
    def perimeter(self):
        directions = Point(0, 1), Point(1, 0), Point(0, -1), Point(-1, 0)
        external = 0
        for p in self.points:
            for d in directions:
                if p + d not in self.points:
                    external += 1
        return external

    @property
    def sides(self):
        from itertools import product
        inner, outer = 0, 0

        n, e, s, w = Point(-1, 0), Point(0, 1), Point(1, 0), Point(0, -1)
        # A point is a corner if none of its neighbors in one quadrant are present
        check = (w, w+n, n), (n, n+e, e), (e, s+e, s), (s, s+w, w)
        for p in self.points:
            outer += sum(not any(p + x in self.points for x in z) for z in check)

        # A point outside of the area is next to an inner corner the two orthogonal
        # neighbors are present
        check = (w, n), (n, e), (e, s), (s, w)
        xmin, xmax, ymin, ymax = self.limits()
        for x, y in product(range(xmin-1, xmax+2), range(ymin-1, ymax+2)):
            p = Point(x, y)
            if p not in self.points:
                inner += sum(all(p + x in self.points for x in z) for z in check)

        return inner + outer

    def limits(self):
        xmin = min(p.x for p in self.points)
        xmax = max(p.x for p in self.points)
        ymin = min(p.y for p in self.points)
        ymax = max(p.y for p in self.points)
        return xmin, xmax, ymin, ymax

    def board(self):
        xmin, xmax, ymin, ymax = self.limits()
        b = [[' ' for _ in range(xmin, xmax+1)] for _ in range(ymin, ymax+1)]
        for p in self.points:
            b[p.y - ymin][p.x - xmin] = self.name
        return b

    def fence_cost(self):
        return self.area * self.perimeter

    def discount_fence_cost(self):
        return self.area * self.sides

    def __str__(self):
        return '\n'.join(''.join(line) for line in self.board())


@dataclass
class Map:
    board: tuple[tuple[chr, ...], ...]
    nx: int = None
    ny: int = None
    regions: tuple[Region, ...] = field(default_factory=tuple)
    
    def __str__(self):
        return '\n'.join(''.join(line) for line in self.board)

    @classmethod
    def from_lines(cls, lines: list[str]):
        nx = len(lines[0])
        assert all(len(line) == nx for line in lines)
        return cls(tuple(tuple(x for x in line) for line in lines))

    def __post_init__(self):
        self.ny = len(self.board)
        self.nx = len(self.board[0])
        if len(self.regions) == 0:
            self.regions = self.find_regions()

    def variety(self, x: Point):
        return self.board[x.y][x.x] if 0 <= x.x < self.nx and 0 <= x.y < self.ny else '.'

    def explore_region(self, p: Point):
        from collections import deque
        directions = Point(0, 1), Point(1, 0), Point(0, -1), Point(-1, 0)
        q = deque()
        q.append(p)
        v = self.variety(p)
        inside = {p}
        while len(q):
            x = q.popleft()
            for d in directions:
                if self.variety(y:=x+d) == v and y not in inside:
                    inside.add(y)
                    q.append(y)
        return Region(v, inside)

    def find_regions(self):
        from itertools import product
        available = [[True for _ in line] for line in self.board]
        region_list = []
        for x, y in product(range(self.nx), range(self.ny)):
            if not available[y][x]:
                continue
            region = self.explore_region(Point(x, y))
            for p in region.points:
                available[p.y][p.x] = False
            region_list.append(region)
        return tuple(region_list)

    def fence_cost(self):
        return sum(r.fence_cost() for r in self.regions)
    
    def discount_fence_cost(self):
        return sum(r.discount_fence_cost() for r in self.regions)


def part1(lines: list[str]) -> int:
    m = Map.from_lines(lines)
    return m.fence_cost()


def part2(lines: list[str]) -> int:
    m = Map.from_lines(lines)
    return m.discount_fence_cost()


if __name__ == '__main__':
    from faoci.interface import fetch_lines
    from timer import Timer

    assert part1(load_txt_lines('example0')) == 140
    assert part1(load_txt_lines('example1')) == 772
    assert part1(load_txt_lines('example2')) == 1930
    assert part2(load_txt_lines('example0')) == 80
    assert part2(load_txt_lines('example1')) == 436
    assert part2(load_txt_lines('exampleE')) == 236
    assert part2(load_txt_lines('example8')) == 368
    assert part2(load_txt_lines('example2')) == 1206

    with Timer(text="\telapsed time {:0.2f} s") as t:
        print(f'Part 1: {part1(fetch_lines(year=2024, day=12))}')

    with Timer(text="\telapsed time {:0.2f} s") as t:
        print(f'Part 2: {part2(fetch_lines(year=2024, day=12))}')
