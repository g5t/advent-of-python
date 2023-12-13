from __future__ import annotations
from dataclasses import dataclass


@dataclass
class AshMap:
    _map: list[list[int]]
    _ignore: int | None = None
    _value: int = 0

    def __post_init__(self):
        if (v := self.vertical_reflection()) is not None:
            self._value = v
        if (h := self.horizontal_reflection()) is not None:
            self._value = 100 * h

    @property
    def value(self):
        return self._value

    @property
    def cols(self):
        return len(self._map[0])

    @property
    def rows(self):
        return len(self._map)

    def check_vertical(self, col) -> bool:
        for c in range(col):
            for r in range(self.rows):
                if col + c < self.cols and self._map[r][col-c-1] != self._map[r][col+c]:
                    return False
        return True

    def check_horizontal(self, row) -> bool:
        for r in range(row):
            for c in range(self.cols):
                if row + r < self.rows and self._map[row-r-1][c] != self._map[row+r][c]:
                    return False
        return True

    def vertical_reflection(self) -> int | None:
        for i in range(1, self.cols):
            if (self._ignore is None or i != self._ignore) and self.check_vertical(i):
                return i
        return None

    def horizontal_reflection(self) -> int | None:
        for i in range(1, self.rows):
            if (self._ignore is None or 100 * i != self._ignore) and self.check_horizontal(i):
                return i
        return None

    def clean(self):
        """By design, every AshMap can have _one_ position flipped and remain a valid AshMap. Find it."""
        from itertools import product
        for (i, j) in product(range(self.rows), range(self.cols)):
            self._map[i][j] = 0 if self._map[i][j] else 1
            # pass the value of the smudged map to avoid re-finding the same reflection
            cleaned = AshMap(self._map, self.value)
            if cleaned.value:
                return cleaned
            self._map[i][j] = 0 if self._map[i][j] else 1
        raise ValueError('AshMap can not be cleaned!')

    @classmethod
    def decode_input(cls, lines: list[str]):
        out = []
        one = []
        for line in lines:
            if len(line.strip()):
                one.append([1 if '#' == x else 0 for x in line.strip()])
            else:
                out.append(cls(one))
                one = []
        if len(one):
            out.append(cls(one))
        return out

    @classmethod
    def from_file(cls, filename):
        with open(filename, 'r') as file:
            return AshMap.decode_input(file.read().splitlines())


def part1(ash: list[AshMap]):
    return sum(a.value for a in ash)


def part2(ash: list[AshMap]):
    return sum(a.clean().value for a in ash)


if __name__ == '__main__':
    assert [a.value for a in AshMap.from_file('y23d13.test')] == [5, 400]
    assert part1(AshMap.from_file('y23d13.test')) == 405
    assert [a.clean().value for a in AshMap.from_file('y23d13.test')] == [300, 100]
    assert part2(AshMap.from_file('y23d13.test')) == 400

    print(part1(AshMap.from_file('y23d13.txt')))
    print(part2(AshMap.from_file('y23d13.txt')))
