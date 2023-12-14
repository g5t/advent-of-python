# Path: /home/gst/PycharmProjects/aoc23/src/23/14/y23d14.py
# Puzzle Source: https://adventofcode.com/2023/day/14
from dataclasses import dataclass
from functools import cache

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
class RockBoard:
    _board: list[list[int]]
    _rocks: list[tuple[int, int]]

    def __eq__(self, other):
        if not all(all(a == b for a, b in zip(row, orow)) for row, orow in zip(self._board, other._board)):
            return False
        return hash(self) == hash(other)

    def __hash__(self):
        # rocks are fungible
        values = tuple(sorted(r[0]*self.cols + r[1] for r in self._rocks))
        return hash(values)

    @property
    def rows(self):
        return len(self._board)

    @property
    def cols(self):
        return len(self._board[0])

    def column(self, c):
        return [r[c] for r in self._board]

    def row(self, r):
        return self._board[r]

    def column_rock_groups(self, c):
        col = [r for r in self._rocks if r[1] == c]
        fixed = [-1, *[i for i, b in enumerate(self.column(c)) if b], self.rows]  # enforce the borders
        groups = [[c for c in col if fixed[i] < c[0] < fixed[i + 1]] for i in range(len(fixed) - 1)]
        return fixed, groups

    def row_rock_groups(self, r):
        rr = [rock for rock in self._rocks if rock[0] == r]
        fixed = [-1, *[i for i, b in enumerate(self.row(r)) if b], self.cols]
        groups = [[rock for rock in rr if fixed[i] < rock[1] < fixed[i+1]] for i in range(len(fixed) - 1)]
        return fixed, groups

    def tilt_north(self):
        rocks = []
        for c in range(self.cols):
            fixed, groups = self.column_rock_groups(c)
            for i in range(len(fixed)-1):
                j = fixed[i] + 1
                row_rocks = [(r, c) for r in range(j, j + len(groups[i]))]
                rocks.extend(row_rocks)
        return RockBoard(self._board, rocks)

    def tilt_south(self):
        rocks = []
        for c in range(self.cols):
            fixed, groups = self.column_rock_groups(c)
            for i in reversed(range(len(fixed) - 1)):
                j = fixed[i+1] - 1
                rocks.extend([(r, c) for r in range(j, j - len(groups[i]), -1)])
        return RockBoard(self._board, rocks)

    def tilt_east(self):
        rocks = []
        for r in range(self.rows):
            fixed, groups = self.row_rock_groups(r)
            for i in reversed(range(len(fixed) - 1)):
                j = fixed[i + 1] - 1
                rocks.extend([(r, c) for c in range(j, j - len(groups[i]), -1)])
        return RockBoard(self._board, rocks)

    def tilt_west(self):
        rocks = []
        for r in range(self.rows):
            fixed, groups = self.row_rock_groups(r)
            for i in range(len(fixed)-1):
                j = fixed[i] + 1
                row_rocks = [(r, c) for c in range(j, j + len(groups[i]))]
                rocks.extend(row_rocks)
        return RockBoard(self._board, rocks)

    @cache
    def one_spin(self):
        return self.tilt_north().tilt_west().tilt_south().tilt_east()

    def spin_load(self, n=1):
        if n < 1:
            return self
        start = hash(self)
        spun = self.one_spin()
        end = hash(spun)
        seen = {start, end}
        path = {start: end}
        loads = {start: self.north_load(), end: spun.north_load()}

        # find the cycle
        cycle = 0
        for i in range(1, n):
            start = end
            spun = spun.one_spin()
            end = hash(spun)
            if end in seen:
                cycle = i + 1
                path[start] = end
                break
            seen.add(end)
            path[start] = end
            loads[end] = spun.north_load()

        print(f'Pattern cycles after {cycle} iterations')
        lead_in = 0
        if end != hash(self):
            count = 0
            a = end
            while path[a] != end and count < cycle:
                a = path[a]
                count += 1
            if count >= cycle:
                raise RuntimeError("How did this happen?")
            lead_in = cycle - count - 1
            cycle = count + 1
            print(f'But it is a lead in of {lead_in} followed by cycles of {cycle}')

        goal = (n - lead_in) % cycle
        a = hash(self)
        for _ in range(lead_in):
            a = path[a]
        for _ in range(goal):
            a = path[a]
        return loads[a]

    def north_load(self):
        n = self.rows
        return sum(n - rock[0] for rock in self._rocks)

    @classmethod
    def from_map(cls, map_lines: list[str]):
        for line in map_lines[1:]:
            if len(line) != len(map_lines[0]):
                raise ValueError("Inconsistent map data")
        rocks = [[1 if '#' == c else 0 for c in line] for line in map_lines]
        rolls = [(r, c) for r, row in enumerate(map_lines) for c, x in enumerate(row) if 'O' == x]
        return RockBoard(rocks, rolls)

    def __str__(self):
        rocks = [['#' if c else '.' for c in row] for row in self._board]
        for rock in self._rocks:
            if rocks[rock[0]][rock[1]] != '.':
                raise ValueError('Setting a non-empty board position to a rolling rock')
            rocks[rock[0]][rock[1]] = 'O'
        return '\n'.join(''.join(r) for r in rocks)


def part1(lines: list[str]) -> int:
    board = RockBoard.from_map(lines)
    tilted = board.tilt_north()
    return tilted.north_load()


def part2(lines: list[str]) -> int:
    return RockBoard.from_map(lines).spin_load(1000000000)


if __name__ == '__main__':
    from faoci.interface import fetch_lines

    assert part1(get_lines('y23d14.test')) == 136
    assert part2(get_lines('y23d14.test')) == 64

    puzzle = fetch_lines(year=2023, day=14)
    print(f'Part 1: {part1(puzzle)}')
    print(f'Part 2: {part2(puzzle)}')
