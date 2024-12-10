# Path: /home/g/Code/advent-of-python/src/24/10/y24d10.py
# Puzzle Source: https://adventofcode.com/2024/day/10
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
class TopoMap:
    topo: tuple[tuple[int, ...], ...] = field(default_factory=tuple)

    @property
    def nx(self):
        return len(self.topo[0])

    @property
    def ny(self):
        return len(self.topo)

    def at(self, p: Point) -> int:
        return self.topo[p.y][p.x]

    @classmethod
    def from_lines(cls, lines: list[str]):
        nx = len(lines[0])
        assert all(len(line) == nx for line in lines)
        topo = tuple(tuple(int(h) for h in line) for line in lines)
        return cls(topo)

    def trailheads(self) -> list[Point]:
        return [Point(x, y) for y, line in enumerate(self.topo) for x, h in enumerate(line) if h == 0]

    def next(self, p: Point) -> list[Point]:
        def is_in(t: Point):
            return 0 <= t.x < self.nx and 0 <= t.y < self.ny
        dirs = Point(0, 1), Point(1, 0), Point(0, -1), Point(-1, 0)
        goal = self.at(p) + 1
        return [n for n in [p + d for d in dirs] if is_in(n) and self.at(n) == goal]



@dataclass
class HikingMap:
    topo: TopoMap

    def explore(self, p: Point):
        from collections import deque
        up_next = deque([(n, p) for n in self.topo.next(p)])
        visited = {p: (0, p)}
        while len(up_next):
            n, c = up_next.pop()
            if (s := visited[c][0] + 1) < visited.get(n, (s+1, n))[0]:
                visited[n] = s, c
                up_next.extend((nn, n) for nn in self.topo.next(n))
        ends = [x for x in visited if self.topo.at(x) == 9]
        # here's where we could walk the paths backwards...
        return len(ends)

    def peruse(self, p: Point, history: tuple[Point, ...]):
        if self.topo.at(p) == 9:
            return (history,)
        return set(p for n in self.topo.next(p) for p in self.peruse(n, history + (n,)))

    def rate(self, p: Point):
        return len(self.peruse(p, (p,)))

    def score_trailheads(self):
        return [self.explore(head) for head in self.topo.trailheads()]

    def rate_trailheads(self):
        return [self.rate(head) for head in self.topo.trailheads()]



def part1(lines: list[str]) -> int:
    return sum(HikingMap(TopoMap.from_lines(lines)).score_trailheads())


def part2(lines: list[str]) -> int:
    return sum(HikingMap(TopoMap.from_lines(lines)).rate_trailheads())


if __name__ == '__main__':
    from faoci.interface import fetch_lines
    from timer import Timer

    assert part1(load_txt_lines('example')) == 36
    assert part2(load_txt_lines('example')) == 81

    with Timer(text="\telapsed time {:0.2f} s") as t:
        print(f'Part 1: {part1(fetch_lines(year=2024, day=10))}')

    with Timer(text="\telapsed time {:0.2f} s") as t:
        print(f'Part 2: {part2(fetch_lines(year=2024, day=10))}')
