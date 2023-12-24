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
class InfiniteMark:
    pos: tuple[int, int]
    neighbors: tuple[tuple[int, bool], ...]


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
    _grid: tuple[InfiniteMark, ...]
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
        nr = len(rows)
        nc = len(rows[0])
        for i, j in product(range(nr), range(nc)):
            if is_field[i][j]:
                nrs[(i, j)] = count
                count += 1
            if 'S' == rows[i][j]:
                start = i, j
        fields = []
        for i, row in enumerate(is_field):
            for j, x in enumerate(row):
                if x:
                    neighbors = [(nrs[((i+x) % nc, (j+y) % nr)], (i+x, j+y) in nrs) for x, y in ((1, 0), (0, 1), (-1, 0), (0, -1)) if ((i+x) % nc, (j+y) % nr) in nrs]
                    fields.append(InfiniteMark(pos=(i, j), neighbors=tuple(neighbors)))
        return InfiniteMarkGrid(tuple(fields), nrs[start], nr, nc)

    def pos_is_field(self, pos: tuple[int, int]):
        for field in self._grid:
            if pos == field.pos:
                return True
        return False

    def field_index(self, pos: tuple[int, int]):
        p = pos[0] % self.rows, pos[1] % self.cols
        for i, field in enumerate(self._grid):
            if p == field.pos:
                return i
        return -1

    def indexes(self):
        from itertools import product
        return product(range(self.rows), range(self.cols))

    def to_char_array(self):
        return [['.' if self.pos_is_field((i, j)) else '#' for j in range(self.cols)] for i in range(self.rows)]

    def __str__(self):
        return '\n'.join(''.join(row) for row in self.to_char_array())

    def step(self, begin: list[tuple[int, tuple[int, int]]]) -> list[int, tuple[int, int]]:
        finish = set()
        for index, pos in begin:
            p_i = self._grid[index].pos
            neighbors = self._grid[index].neighbors
            for n, same_grid in neighbors:
                p_n = self._grid[n].pos
                d_n = p_n[0] - p_i[0], p_n[1] - p_i[1]
                if not same_grid:
                    offset = clamp(d_n[0], -1, 1) * self.rows, clamp(d_n[1], -1, 1) * self.cols
                else:
                    offset = 0, 0
                p_n = pos[0] + d_n[0] + offset[0], pos[1] + d_n[1] + offset[1]
                finish.add((n, p_n))
        return list(finish)

    def find_points(self, points: list[tuple[int, int]], guess: int):
        to_find = [(self.field_index(pos), pos) for pos in points]
        count = 0
        accessible = [(self.start, self._grid[self.start].pos)]
        sequence = [1]
        while not any(o in accessible for o in to_find) and count < 10 * guess:
            accessible = self.step(accessible)
            sequence.append(len(accessible))
            count += 1
        if count >= guess * 10:
            print('Loop exited without finding points')
        if not all(x in accessible for x in to_find):
            raise RuntimeError('Not all points in accessible space')
        return sequence

    def find_square(self):
        outside = [(self.rows-1, self.cols-1), (self.rows-1, 0), (0, self.cols-1), (0, 0)]
        guess = (self.rows + self.cols) // 2
        return self.find_points(outside, guess)

    def find_diamond(self):
        sy, sx = self._grid[self.start].pos
        centers = [(sy + y, sx + x) for (y, x) in ((self.rows, self.cols),
                                                   (-self.rows, -self.cols),
                                                   (-self.rows, self.cols),
                                                   (self.rows, -self.cols))]
        guess = (sy + self.rows + sx + self.cols) // 2
        return self.find_points(centers, guess)

    def run(self, n=26501365):
        square = self.find_square()  # sequence up to filling the first field
        diamond = self.find_diamond()  # sequence up to filling the first neighboring fields (hopefully)
        n_first = len(square) - 1  # first element is the zeroth-step
        n_second = len(diamond) - 1
        # each subsequent full field is filled in
        steps_per_ring = n_second - n_first
        full_rings = (n - n_first) // steps_per_ring
        # each ring adds 4 * n * the difference of accessible space between the zeroth and first rings
        # so the total number of 'differences' added is -> sum(4 * n, 1, N) = 4 * N * (N - 1) / 2
        total_differences = 2 * full_rings * (full_rings - 1)
        extra_steps = (n - n_first) % steps_per_ring
        if extra_steps:
            # we need to figure out which step we end on, and add 4 * (full_rings + 1) times
            # the differential step value, plus figure out which square and diamond to use ...
            raise ValueError('Crap')
        accessible = square[-1] + (diamond[-1] - square[-1]) * total_differences
        return accessible


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
    return field.run()


if __name__ == '__main__':
    from faoci.interface import fetch_lines

    test_field = MarkGrid.from_lines(get_lines('y23d21.test'))
    assert test_field.run(6) == 16

    test_infinite_field = InfiniteMarkGrid.from_lines(get_lines('y23d21.test'))
    assert test_infinite_field.run(6) == 16
    assert test_infinite_field.run(10) == 50
    assert test_infinite_field.run(50) == 1594
    # assert test_infinite_field.run(5000) == 16733044

    puzzle = fetch_lines(year=2023, day=21)
    print(f'Part 1: {part1(puzzle)}')
    print(f'Part 2: {part2(puzzle)}')
