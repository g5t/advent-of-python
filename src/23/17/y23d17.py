# Path: /home/gst/PycharmProjects/aoc23/src/23/17/y23d17.py
# Puzzle Source: https://adventofcode.com/2023/day/17
from __future__ import annotations
from dataclasses import dataclass


@dataclass
class Crucible:
    loss: int
    position: tuple[int, int]
    previous: tuple[int, int]
    straights: int

    @property
    def state(self):
        return self.position, self.previous, self.straights

    def __lt__(self, other):
        return (self.loss, self.straights) < (other.loss, other.straights)


@dataclass
class HeatLossMap:
    _cost: tuple[tuple[int, ...], ...]

    @classmethod
    def from_lines(cls, map_lines: list[str]):
        return HeatLossMap(tuple(tuple(int(c) for c in line) for line in map_lines))

    @property
    def rows(self):
        return len(self._cost)

    @property
    def cols(self):
        return len(self._cost[0])

    def inbound(self, pos: tuple[int, int]):
        return 0 <= pos[0] < self.rows and 0 <= pos[1] < self.cols

    def lost_at(self, pos: tuple[int, int]):
        return self._cost[pos[0]][pos[1]]

    def possible(self, crucible: Crucible, turn_allowed: bool, straight_allowed: bool):
        pos, last = crucible.position, crucible.previous
        d = pos[0] - last[0], pos[1] - last[1]
        p = []
        if turn_allowed and (d == (1, 0) or d == (-1, 0)):
            p.extend([((0, 1), 1), ((0, -1), 1)])
        if turn_allowed and (d == (0, 1) or d == (0, -1)):
            p.extend([((1, 0), 1), ((-1, 0), 1)])
        if straight_allowed:
            p.append((d, crucible.straights + 1))
        p = [((pos[0] + x[0], pos[1] + x[1]), c) for x, c in p]
        return [Crucible(crucible.loss + self.lost_at(x), x, pos, count) for x, count in p if self.inbound(x)]

    def normal_rules(self, crucible: Crucible):
        return self.possible(crucible, True, crucible.straights < 3)

    def ultra_rules(self, crucible: Crucible):
        return self.possible(crucible, crucible.straights > 3, crucible.straights < 10)

    def find_path(self, start: tuple[int, int] | None = None, goal: tuple[int, int] | None = None, normal: bool = True):
        import heapq
        if start is None:
            start = 0, 0
        if goal is None:
            goal = self.rows - 1, self.cols - 1
        options = [(start[0]+p[0], start[1]+p[1]) for p in [(0, 1), (0, -1), (1, 0), (-1, 0)]]
        queue = [Crucible(self.lost_at(pos), pos, start, 1) for pos in options if self.inbound(pos)]
        visited = set()
        while queue:
            crucible = heapq.heappop(queue)
            if crucible.state not in visited:
                visited.add(crucible.state)
                # if we're at the goal _and_ allowed to stop:
                if crucible.position == goal and (normal or crucible.straights > 3):
                    return crucible.loss
                for option in self.normal_rules(crucible) if normal else self.ultra_rules(crucible):
                    heapq.heappush(queue, option)


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
    return HeatLossMap.from_lines(lines).find_path()


def part2(lines: list[str]) -> int:
    return HeatLossMap.from_lines(lines).find_path(normal=False)


if __name__ == '__main__':
    from faoci.interface import fetch_lines

    assert part1(get_lines('y23d17.test')) == 102
    assert part2(get_lines('y23d17.test')) == 94
    assert part2(get_lines('y23d17b.test')) == 71

    puzzle = fetch_lines(year=2023, day=17)
    print(f'Part 1: {part1(puzzle)}')
    print(f'Part 2: {part2(puzzle)}')
