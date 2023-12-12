from dataclasses import dataclass, field

@dataclass
class SparseGalaxy:
    _coords: list[tuple[int, int]] = field(default_factory=list)

    def __str__(self):
        max_r = self.rows
        max_c = self.cols
        board = [['.' for _ in range(max_c)] for _ in range(max_r)]
        for coord in self._coords:
            board[coord[0]][coord[1]] = '*'
        return '\n'.join(''.join(row) for row in board)

    @classmethod
    def from_lines(cls, lines: list[str]):
        from itertools import product
        if any(len(line) != len(lines[0]) for line in lines):
            raise ValueError('Inconsistent input shape')
        galaxies = [(r, c) for r, c in product(range(len(lines)), range(len(lines[0]))) if lines[r][c] == '#']
        return cls(galaxies)

    @property
    def rows(self):
        return max(c[0] for c in self._coords) + 1

    @property
    def cols(self):
        return max(c[1] for c in self._coords) + 1

    def row_sum(self, r):
        return sum(c[0] == r for c in self._coords)

    def col_sum(self, x):
        return sum(c[1] == x for c in self._coords)

    def expand(self, n: int = 1):
        empty_cols = [c for c in range(self.cols) if self.col_sum(c) == 0]
        empty_rows = [r for r in range(self.rows) if self.row_sum(r) == 0]
        for col in reversed(empty_cols):
            for i, coord in enumerate(self._coords):
                if coord[1] > col:
                    self._coords[i] = coord[0], coord[1] + n - 1
        for row in reversed(empty_rows):
            for i, coord in enumerate(self._coords):
                if coord[0] > row:
                    self._coords[i] = coord[0] + n - 1, coord[1]

    def pairwise_distances(self):
        dist = {}
        for i, a in enumerate(self._coords):
            for j, b in enumerate(self._coords):
                if j > i:
                    # manhattan distances
                    dist[(i+1, j+1)] = abs(b[0] - a[0]) + abs(b[1] - a[1])
        return dist


def read_values(filename) -> list[str]:
    from pathlib import Path
    if not Path(filename).exists():
        return []
    with open(filename, 'r') as f:
        return f.readlines()


def solve_puzzle(values, expansion: int = 2):
    galaxy = SparseGalaxy.from_lines(values)
    galaxy.expand(expansion)
    distances = galaxy.pairwise_distances()
    return sum(distances.values())


def part1(values: list[str]):
    return solve_puzzle(values)


def part2(values: list[str]):
    return solve_puzzle(values, 1000000)


if __name__ == '__main__':
    test_values = read_values('y23d11.test')
    assert solve_puzzle(test_values) == 374
    assert part1(test_values) == 374
    assert solve_puzzle(test_values, 10) == 1030
    assert solve_puzzle(test_values, 100) == 8410
    puzzle = read_values('y23d11.txt')
    print(part1(puzzle))
    print(part2(puzzle))
