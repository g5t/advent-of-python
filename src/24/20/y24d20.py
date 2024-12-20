# Path: /home/g/Code/advent-of-python/src/24/20/y24d20.py
# Puzzle Source: https://adventofcode.com/2024/day/20
from dataclasses import dataclass, field
from typing import TypeVar, Any


def load_lines(named: str):
    from pathlib import Path
    with Path(__file__).parent.joinpath(f'{named}.test').open('r') as f:
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

    def __repr__(self):
        return str(self)


class Heap:
    @dataclass(order=True)
    class Item:
        priority: int
        item: Any=field(compare=False)

    def __init__(self):
        self.heap = []
    def push(self, element: Item):
        from heapq import heappush
        heappush(self.heap, element)
    def pop(self):
        from heapq import heappop
        return heappop(self.heap)
    def __len__(self):
        return len(self.heap)


def djikstra(start: Point, graph: dict[Point, dict[Point, int]]):
    queue = Heap()
    distances = {}
    queue.push(Heap.Item(0, start))
    distances[start] = 0
    while len(queue):
        item = queue.pop()
        score, key = item.priority, item.item
        if distances[key] < score or key not in graph:
            continue
        for node, weight in graph[key].items():
            new_score = score + weight
            if distances.get(node, new_score + 1) > new_score:
                distances[node] = new_score
                queue.push(Heap.Item(new_score, node))
    return distances


@dataclass
class Track:
    bitmap: tuple[tuple[int, ...], ...]
    start: Point
    goal: Point
    forward: dict[tuple[Point, Point], dict[tuple[Point, Point], int]] = field(default_factory=dict)
    reverse: dict[tuple[Point, Point], dict[tuple[Point, Point], int]] = field(default_factory=dict)

    @property
    def nx(self):
        return len(self.bitmap[0])

    @property
    def ny(self):
        return len(self.bitmap)

    def at(self, p: Point) -> int:
        return self.bitmap[p.y][p.x]

    @classmethod
    def from_lines(cls, lines: list[str], n: int = 71):
        from itertools import product
        n = len(lines[0])
        assert all(len(line) == n for line in lines)
        bm = [[1 if '#' == c else 0 for c in line] for line in lines]
        start, goal = Point(0, 0), Point(n-1, n-1)
        for i, j in product(range(n), range(len(lines))):
            if 'S' == lines[j][i]:
                start = Point(i, j)
            if 'E' == lines[j][i]:
                goal = Point(i, j)
        return cls(tuple(tuple(row) for row in bm), start, goal)

    def dirs(self):
        return Point(0, 1), Point(1, 0), Point(0, -1), Point(-1, 0)

    def char_map(self):
        return [['#' if x else '.' for x in row] for row in self.bitmap]

    def __str__(self):
        return '\n'.join(''.join(row) for row in self.char_map())

    def spaces(self):
        from itertools import product
        return [Point(x, y) for x, y in product(range(self.nx), range(self.ny)) if self.bitmap[y][x] == 0]

    def ways(self, p: Point, d: Point, value: int = 0):
        n = p + d
        if 0 <= n.x < self.nx and 0 <= n.y < self.ny and self.at(n) == value:
            return ((n, 1), )
        return tuple()

    def build_graphs(self):
        from itertools import product
        for p, d in product(self.spaces(), self.dirs()):
            for n, c in self.ways(p, d):
                self.forward.setdefault(p, {})[n] = c
                self.reverse.setdefault(n, {})[p] = c
    
    def __post_init__(self):
        if not len(self.forward) and not len(self.reverse):
            self.build_graphs()

    def cost(self):
        distances = djikstra(self.start, self.forward)
        return distances.get(self.goal, -1)

    def old_rule_count(self, save: int):
        from itertools import product
        fwd = djikstra(self.start, self.forward)
        rev = djikstra(self.goal, self.reverse)
        count = 0
        for s, d in product(self.spaces(), self.dirs()):
            n = s + d * 2
            if 0 <= n.x < self.nx and 0 <= n.y < self.ny and self.at(s+d) != 0 and self.at(n) == 0:
                if fwd[self.goal] - fwd[s] - rev[n] - 2 >= save:
                    count += 1
        return count

    def metropolis_glitch(self, start: Point, duration: int):
        from itertools import product
        graph = {}
        for dx, dy in product(range(-duration, duration+1), range(-duration, duration+1)):
            p = start + Point(dx, dy)
            if dx and dy and abs(dx) + abs(dy) > duration or not (0 <= p.x < self.nx and 0 <= p.y < self.nx and self.at(p) == 0):
                continue
            graph[p] = abs(dx) + abs(dy)
        return graph

    def glitch_count(self, save: int, duration: int = 20):
        fwd = djikstra(self.start, self.forward)
        rev = djikstra(self.goal, self.reverse)
        counts = {}
        for start in self.spaces():
            for til, dist in self.metropolis_glitch(start, duration).items():
                saved = fwd[self.goal] - fwd[start] - rev[til] - dist
                if saved >= save:
                    counts[saved] = counts.get(saved, 0) + 1
        return counts



def part1(lines: list[str], save: int = 100) -> int:
    from timer import Timer
    with Timer():
        track = Track.from_lines(lines)
        return track.old_rule_count(save)


def part2(lines: list[str], save: int = 100) -> int:
    from timer import Timer
    with Timer():
        track = Track.from_lines(lines)
        return sum(track.glitch_count(save).values())


if __name__ == '__main__':
    from faoci.interface import fetch_lines

    lines = load_lines('y24d20')
    assert Track.from_lines(lines).cost() == 84
    assert part1(lines, 20) == 5
    assert part1(lines, 10) == 10
    assert Track.from_lines(lines).glitch_count(save=10, duration=2) == {64:1, 40:1, 38:1, 36:1, 20:1, 12:3, 10:2}
    assert part2(lines, 74) == 7
    assert Track.from_lines(lines).glitch_count(save=50) == {76: 3, 74: 4, 72: 22, 70: 12, 68: 14, 66: 12, 64: 19, 62: 20, 60: 23, 58: 25, 56: 39, 54: 29, 52: 31, 50: 32}
    assert part2(lines, 50) == sum([3, 4, 22, 12, 14, 12, 19, 20, 23, 25, 39, 29, 31, 32])

    puzzle = fetch_lines(year=2024, day=20)
    print(f'Part 1: {part1(puzzle)}')
    print(f'Part 2: {part2(puzzle)}')
