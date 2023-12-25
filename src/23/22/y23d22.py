# Path: /home/gst/PycharmProjects/aoc23/src/23/22/y23d22.py
# Puzzle Source: https://adventofcode.com/2023/day/22
from dataclasses import dataclass


@dataclass
class Brick:
    at: tuple[tuple[int, int, int], ...]

    def drop(self, dist: int = 1):
        new_at = [(p[0], p[1], p[2] - dist) for p in self.at]
        self.at = tuple(new_at)

    @classmethod
    def from_line(cls, line: str):
        mins, maxs = line.split('~')
        xmin, ymin, zmin = [int(n) for n in mins.split(',')]
        xmax, ymax, zmax = [int(n) for n in maxs.split(',')]
        if xmin == xmax and ymin == ymax and zmin == zmax:
            return cls(((xmin, ymin, zmin),))
        if xmin == xmax and ymin == ymax:
            return cls(tuple((xmin, ymin, z) for z in range(zmin, zmax + 1)))
        if xmin == xmax and zmin == zmax:
            return cls(tuple((xmin, y, zmin) for y in range(ymin, ymax + 1)))
        if zmin == zmax and ymin == ymax:
            return cls(tuple((x, ymin, zmin) for x in range(xmin, xmax + 1)))
        raise ValueError('Non-1D line of bricks?')

    @property
    def zmin(self):
        return min(p[2] for p in self.at)

    @property
    def zmax(self):
        return max(p[2] for p in self.at)

    @property
    def xmin(self):
        return min(p[0] for p in self.at)

    @property
    def xmax(self):
        return max(p[0] for p in self.at)

    @property
    def ymin(self):
        return min(p[1] for p in self.at)

    @property
    def ymax(self):
        return max(p[1] for p in self.at)

    def __lt__(self, other):
        return self.zmin < other.zmin

    def supports(self, other):
        for p in self.at:
            if (p[0], p[1], p[2] + 1) in other.at:
                return True
        return False


@dataclass
class BrickStack:
    stack: tuple[Brick, ...]

    def code(self, index: int, pad: int = 1):
        if index < 0:
            return '.' * pad
        if index >= len(self.stack):
            return '?' * pad
        c = []
        alpha = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
        index += 1
        while index:
            index, rem = divmod(index - 1, 26)
            c[:0] = alpha[rem]
        return f"{''.join(c):{pad}s}"

    def to_lines(self):
        (x_min, x_max), (y_min, y_max), (z_min, z_max) = self.limits()
        nb = len(self.stack)
        x_proj = [[-nb for _ in range(x_min, x_max + 1)] for _ in range(z_min, z_max + 1)]
        y_proj = [[-nb for _ in range(y_min, y_max + 1)] for _ in range(z_min, z_max + 1)]
        for i, brick in self.enumerated():
            for x, y, z in brick.at:
                if x_proj[z - z_min][x - x_min] != i:
                    x_proj[z - z_min][x - x_min] += nb + i
                if y_proj[z - z_min][y - y_min] != i:
                    y_proj[z - z_min][y - y_min] += nb + i
        nz = max(len(str(z_min)), len(str(z_max)))
        nw = len(self.code(len(self.stack)-1))
        first = (' '*(nz + 2)
                 + ''.join(f'{x:{nw}d}' for x in range(x_min, x_max + 1))
                 + '  '
                 + ''.join(f'{y:{nw}d}' for y in range(y_min, y_max + 1)))
        lines = [first]
        for x, y, z in zip(reversed(x_proj), reversed(y_proj), reversed(range(z_min, z_max + 1))):
            lines.append(f'{z:{nz}d}  ' + ''.join(self.code(i, nw) for i in x) + '  ' + ''.join(self.code(i, nw) for i in y))
        return lines

    def __str__(self):
        return '\n'.join(self.to_lines())

    @classmethod
    def from_lines(cls, lines: list[str]):
        return cls(tuple(sorted([Brick.from_line(line) for line in lines])))

    def resort(self):
        self.stack = tuple(sorted(self.stack))

    def empty_lists(self):
        return {i: [] for i in range(len(self.stack))}

    def enumerated(self):
        return enumerate(self.stack)

    def indexes(self):
        return range(len(self.stack))

    def limits(self):
        xmin = min(x.xmin for x in self.stack)
        xmax = max(x.xmax for x in self.stack)
        ymin = min(x.ymin for x in self.stack)
        ymax = max(x.ymax for x in self.stack)
        zmin = min(x.zmin for x in self.stack)
        zmax = max(x.zmax for x in self.stack)
        return (xmin, xmax), (ymin, ymax), (zmin, zmax)


@dataclass
class BrickNetwork:
    stack: BrickStack
    parents: dict[int, list[int]]
    children: dict[int, list[int]]

    @classmethod
    def from_lines(cls, lines: list[str]):
        bricks = BrickStack.from_lines(lines)
        stuck = set()

        def droppable(b: Brick):
            return not any((p[0], p[1], p[2] - 1) in stuck or p[2] - 1 < 0 for p in b.at)

        for brick in bricks.stack:
            while droppable(brick):
                brick.drop()
            stuck.update(brick.at)

        bricks.resort()
        children = bricks.empty_lists()
        parents = bricks.empty_lists()
        for i, first in bricks.enumerated():
            for j, second in bricks.enumerated():
                if second.zmin > first.zmax + 1:
                    break
                if j > i and first.supports(second):
                    parents[j].append(i)
                    children[i].append(j)

        return cls(bricks, parents, children)

    def removable(self):
        single_support_of = self.stack.empty_lists()
        for i in self.stack.indexes():
            for j in self.stack.indexes():
                if self.parents[j] == [i]:
                    single_support_of[i].append(j)
        return [i for i in self.stack.indexes() if len(single_support_of[i]) == 0]

    def chain_sizes(self):
        cs = {}
        for i in self.stack.indexes():
            visit = set(self.children[i])
            fallen = {i}
            while len(visit):
                j = visit.pop()
                if all(x in fallen for x in self.parents[j]):
                    visit.update(self.children[j])
                    fallen.add(j)
            if len(fallen) > 1:
                cs[i] = len(fallen) - 1
        return cs


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
    stack = BrickNetwork.from_lines(lines)
    return len(stack.removable())


def part2(lines: list[str]) -> int:
    stack = BrickNetwork.from_lines(lines)
    chains = stack.chain_sizes()
    return sum(chains.values())


if __name__ == '__main__':
    from faoci.interface import fetch_lines

    test_stack = BrickNetwork.from_lines(get_lines('y23d22.test'))
    assert test_stack.removable() == [1, 2, 3, 4, 6]
    assert part1(get_lines('y23d22.test')) == 5
    assert part2(get_lines('y23d22.test')) == 7

    puzzle = fetch_lines(year=2023, day=22)
    network = BrickNetwork.from_lines(puzzle)

    print(f'Part 1: {part1(puzzle)}')
    print(f'Part 2: {part2(puzzle)}')
