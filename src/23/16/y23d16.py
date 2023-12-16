# Path: /home/gst/PycharmProjects/aoc23/src/23/16/y23d16.py
# Puzzle Source: https://adventofcode.com/2023/day/16
from __future__ import annotations
from dataclasses import dataclass, field
from enum import Enum, auto


def get_lines(filename):
    from pathlib import Path
    if isinstance(filename, str):
        filename = Path(filename)
    filename = filename.resolve()
    if not filename.exists():
        return []

    with open(filename, 'r') as file:
        return file.read().splitlines()


class Type(Enum):
    blank = auto()
    back = auto()
    forward = auto()
    vertical = auto()
    horizontal = auto()

    @classmethod
    def from_char(cls, c: str):
        m = {'.': Type.blank, '\\': Type.back, '/': Type.forward, '|': Type.vertical, '-': Type.horizontal}
        return m[c]

    def __str__(self):
        m = {Type.blank: '.', Type.back: '\\', Type.forward: '/', Type.vertical: '|', Type.horizontal: '-'}
        return m[self]

    def directions(self, incoming: tuple[int, int]) -> list[tuple[int, int]]:
        if Type.back == self:
            return [(incoming[1], 0)] if incoming[1] else [(0, incoming[0])]
        if Type.forward == self:
            return [(-incoming[1], 0)] if incoming[1] else [(0, -incoming[0])]
        if Type.vertical == self:
            return [(1, 0), (-1, 0)] if incoming[1] else [incoming]
        if Type.horizontal == self:
            return [(0, 1),  (0, -1)] if incoming[0] else [incoming]
        return [incoming]


@dataclass
class MirrorGrid:
    _grid: tuple[tuple[Type, ...], ...]
    rows: int = 0
    cols: int = 0

    def __post_init__(self):
        self.rows = len(self._grid)
        self.cols = len(self._grid[0])
        if any(len(x) != self.cols for x in self._grid):
            raise ValueError('Inconsistent mirror grid')

    @classmethod
    def from_lines(cls, grid_lines: list[str]):
        grid = tuple(tuple(Type.from_char(c) for c in line) for line in grid_lines)
        return MirrorGrid(grid)

    def to_lines(self):
        return [''.join(str(c) for c in line) for line in self._grid]

    def to_lists(self):
        return [[str(c) for c in line] for line in self._grid]

    def is_blank(self, position: tuple[int, int]):
        if 0 <= position[0] < self.rows and 0 <= position[1] < self.cols:
            return Type.blank == self._grid[position[0]][position[1]]
        return False

    def directions(self, position: tuple[int, int], incoming: tuple[int, int]) -> list[tuple[int, int]]:
        if 0 <= position[0] < self.rows and 0 <= position[1] < self.cols:
            return self._grid[position[0]][position[1]].directions(incoming)
        return []


@dataclass
class Ray:
    position: tuple[int, int]
    direction: tuple[int, int]

    def __hash__(self):
        return hash(self.position + self.direction)

    def step(self):
        self.position = self.position[0] + self.direction[0], self.position[1] + self.direction[1]


@dataclass
class Tracer:
    _grid: MirrorGrid
    _energized: list[list[int]] = field(default_factory=list)

    @classmethod
    def from_lines(cls, grid_lines: list[str]):
        return Tracer(MirrorGrid.from_lines(grid_lines))

    def __post_init__(self):
        self._energized = [[0 for c in range(self._grid.cols)] for r in range(self._grid.rows)]

    def __str__(self):
        from itertools import product
        lines = self._grid.to_lists()
        for r, c in product(range(self._grid.rows), range(self._grid.cols)):
            if self._energized[r][c] and self._grid.is_blank((r, c)):
                lines[r][c] = 'x'
            if self._energized[r][c]:
                lines[r][c] = f'\033[36m{lines[r][c]}\033[0;39m'
        return '\n'.join(''.join(line) for line in lines)

    def reset(self):
        from itertools import product
        for (r, c) in product(range(self._grid.rows), range(self._grid.cols)):
            self._energized[r][c] = 0

    def trace(self, start: Ray | None = None, update_plot: bool = False):
        rays = [Ray((0, 0), (0, 1))] if start is None else [start]
        memory = set()
        visited = set()
        while len(rays):
            while len(rays) and hash(rays[0]) in memory:
                rays.pop(0)
            if len(rays):
                visited.add(rays[0].position)
                memory.add(hash(rays[0]))
                ds = self._grid.directions(rays[0].position, rays[0].direction)
                if len(ds):
                    rays[0].direction = ds[0]
                    if len(ds) == 2:
                        rays.append(Ray(rays[0].position, ds[1]))
                    rays[0].step()  # ensure we take a step before checking if blank
                    visited.add(rays[0].position)
                    while self._grid.is_blank(rays[0].position):
                        rays[0].step()
                        visited.add(rays[0].position)
        energized = [v for v in visited if 0 <= v[0] < self._grid.rows and 0 <= v[1] < self._grid.cols]
        if update_plot:
            self.reset()
            for (r, c) in energized:
                self._energized[r][c] = 1
        return len(energized)

    def trace_edges(self):
        top = [((0, i), (1, 0)) for i in range(self._grid.cols)]
        left = [((i, 0), (0, 1)) for i in range(self._grid.rows)]
        right = [((i, self._grid.cols-1), (0, -1)) for i in range(self._grid.rows)]
        bottom = [((self._grid.rows-1, i), (-1, 0)) for i in range(self._grid.cols)]
        return max([self.trace(start=Ray(*x)) for x in [*top, *left, *right, *bottom]])


def part1(lines: list[str]) -> int:
    tracer = Tracer.from_lines(lines)
    return tracer.trace()


def part2(lines: list[str]) -> int:
    tracer = Tracer.from_lines(lines)
    return tracer.trace_edges()


if __name__ == '__main__':
    from faoci.interface import fetch_lines

    assert part1(get_lines('y23d16.test')) == 46
    assert part1(get_lines('y23d16a.test')) == 36
    assert part1(get_lines('y23d16b.test')) == 36
    assert part1(get_lines('y23d16c.test')) == 36
    assert part1(get_lines('y23d16d.test')) == 36
    assert part1(get_lines('y23d16e.test')) == 20
    assert part1(get_lines('y23d16f.test')) == 20
    assert part1(get_lines('y23d16g.test')) == 23
    assert part2(get_lines('y23d16.test')) == 51

    puzzle = fetch_lines(year=2023, day=16)
    print(f'Part 1: {part1(puzzle)}')
    print(f'Part 2: {part2(puzzle)}')
