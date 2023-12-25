# Path: /home/gst/PycharmProjects/aoc23/src/23/21/y23d21.py
# Puzzle Source: https://adventofcode.com/2023/day/21
from dataclasses import dataclass

def clamp(value, minimum, maximum):
    if value < minimum:
        return minimum
    if value > maximum:
        return maximum
    return value


@dataclass
class Mark:
    pos: tuple[int, int]
    neighbors: tuple[int, ...]


@dataclass
class MarkGrid:
    _grid: tuple[Mark, ...]
    start: int
    rows: int = 0
    cols: int = 0

    @classmethod
    def from_lines(cls, rows: list[str]):
        from itertools import product
        is_field = [['.' == x or 'S' == x for x in row] for row in rows]
        nrs = {}
        count = 0
        start = -1, -1
        for i, j in product(range(len(rows)), range(len(rows[0]))):
            if is_field[i][j]:
                nrs[(i, j)] = count
                count += 1
            if 'S' == rows[i][j]:
                start = i, j
        fields = []
        for i, row in enumerate(is_field):
            for j, x in enumerate(row):
                if x:
                    neighbors = [nrs[(i+x, j+y)] for x, y in ((1, 0), (0, 1), (-1, 0), (0, -1)) if (i+x, j+y) in nrs]
                    fields.append(Mark(pos=(i, j), neighbors=tuple(neighbors)))
        return MarkGrid(tuple(fields), nrs[start], len(rows), len(rows[0]))

    def pos_is_field(self, pos: tuple[int, int]):
        for field in self._grid:
            if pos == field.pos:
                return True
        return False

    def indexes(self):
        from itertools import product
        return product(range(self.rows), range(self.cols))

    def to_char_array(self):
        return [['.' if self.pos_is_field((i, j)) else '#' for j in range(self.cols)] for i in range(self.rows)]

    def __str__(self):
        return '\n'.join(''.join(row) for row in self.to_char_array())

    def step(self, begin: list[int]) -> list[int]:
        finish = set()
        for index in begin:
            finish.update(self._grid[index].neighbors)
        return list(finish)

    def run(self, n=64):
        accessible = [self.start]
        for i in range(n):
            accessible = self.step(accessible)
        return len(accessible)


@dataclass
class InfiniteMarkGrid:
    _grid: tuple[tuple[bool, ...], ...]
    start: tuple[int, int]
    rows: int = 0
    cols: int = 0

    @classmethod
    def from_lines(cls, rows: list[str]):
        from itertools import product
        is_field = tuple([tuple(['.' == x or 'S' == x for x in row]) for row in rows])
        start = -1, -1
        nr = len(rows)
        nc = len(rows[0])
        for i, j in product(range(nr), range(nc)):
            if 'S' == rows[i][j]:
                start = i, j
        return InfiniteMarkGrid(is_field, start, nr, nc)

    def pos_is_field(self, pos: tuple[int, int]):
        return self._grid[pos[0] % self.rows][pos[1] % self.cols]

    def field_index(self, pos: tuple[int, int]):
        p = pos[0] % self.rows, pos[1] % self.cols
        return p

    def indexes(self):
        from itertools import product
        return product(range(self.rows), range(self.cols))

    def to_char_array(self):
        return [['.' if self.pos_is_field((i, j)) else '#' for j in range(self.cols)] for i in range(self.rows)]

    def __str__(self):
        return '\n'.join(''.join(row) for row in self.to_char_array())

    def neighbors(self, pos: tuple[int, int]):
        for d in ((0, -1), (0, 1), (1, 0), (-1, 0)):
            p = pos[0] + d[0], pos[1] + d[1]
            if self.pos_is_field(p):
                yield p

    def step(self, begin: list[tuple[int, int]]) -> list[tuple[int, int]]:
        finish = set()
        for pos in begin:
            finish.update(list(self.neighbors(pos)))
        return list(finish)

    def run(self, ns: list[int]):
        accessible = [self.start]
        vals = [0 for _ in ns]
        for i in range(max(ns)):
            accessible = self.step(accessible)
            if i + 1 in ns:
                vals[ns.index(i + 1)] = len(accessible)
        return vals

    def estimate(self, n=26501365):
        if self.rows != self.cols:
            print('Expected square input')
        half = self.rows // 2
        x = [half + self.rows * i for i in range(3)]
        print(f'{x=}')
        y = self.run(x)
        print(f'{y=}')

        def f(p, m):
            a = (p[2] - (2 * p[1]) + p[0]) // 2
            b = p[1] - p[0] - a
            c = p[0]
            return a * m * m + b * m + c

        return f(y, (n - half) // self.rows)


def get_lines(filename):
    from pathlib import Path
    if isinstance(filename, str):
        filename = Path(filename)
    filename = filename.resolve()
    if not filename.exists():
        return []

    with open(filename, 'r') as file:
        return file.read().splitlines()


def part1(lines: list[str]) -> int:
    field = MarkGrid.from_lines(lines)
    return field.run()


def part2(lines: list[str]) -> int:
    field = InfiniteMarkGrid.from_lines(lines)
    return field.estimate()


if __name__ == '__main__':
    from faoci.interface import fetch_lines

    test_field = MarkGrid.from_lines(get_lines('y23d21.test'))
    assert test_field.run(6) == 16

    test_infinite_field = InfiniteMarkGrid.from_lines(get_lines('y23d21.test'))
    # assert test_infinite_field.estimate(6) == 16
    # assert test_infinite_field.estimate(10) == 50
    # assert test_infinite_field.estimate(50) == 1594
    # assert test_infinite_field.estimate(5000) == 16733044

    puzzle = fetch_lines(year=2023, day=21)
    print(f'Part 1: {part1(puzzle)}')
    print(f'Part 2: {part2(puzzle)}')  # less than 10451259239628549432
