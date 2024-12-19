# Path: /home/g/Code/advent-of-python/src/24/18/y24d18.py
# Puzzle Source: https://adventofcode.com/2024/day/18
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


@dataclass
class Space:
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
        bm = [[0 for _ in range(n)] for _ in range(n)]
        start, goal = Point(0, 0), Point(n-1, n-1)
        for i, line in enumerate(lines):
            x, y = [int(c) for c in line.split(',')]
            bm[y][x] = i + 1
        return cls(tuple(tuple(row) for row in bm), start, goal)

    def first(self, n):
        return Space(tuple(tuple(0 if v > n else v for v in row) for row in self.bitmap), self.start, self.goal)

    def dirs(self):
        return Point(0, 1), Point(1, 0), Point(0, -1), Point(-1, 0)

    def char_map(self):
        return [['#' if x else '.' for x in row] for row in self.bitmap]

    def __str__(self):
        return '\n'.join(''.join(row) for row in self.char_map())

    def spaces(self):
        from itertools import product
        return [Point(x, y) for x, y in product(range(self.nx), range(self.ny)) if self.bitmap[y][x] == 0]

    def ways(self, p: Point, d: Point):
        n = p + d
        if 0 <= n.x < self.nx and 0 <= n.y < self.ny and self.at(n) == 0:
            return ((n, 1), )
        return tuple()

    def build_graphs(self):
        from itertools import product
        for p, d in product(self.spaces(), self.dirs()):
            fkey = p
            for n, c in self.ways(p, d):
                self.forward.setdefault(p, {})[n] = c
                self.reverse.setdefault(n, {})[p] = c
    
    def __post_init__(self):
        self.build_graphs()

    def djikstra(self, start: Point, graph: dict[Point, dict[Point, int]]):
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

    def cost(self):
        distances = self.djikstra(self.start, self.forward)
        return distances.get(self.goal, -1)

def close_search(space: Space, at_least: int, n: int, at_most: int):
    cost = space.first(n).cost()
    if cost < 0:
        return close_search(space, at_least, at_least + (n - at_least) // 2, n - 1)
    cost = space.first(n+1).cost()
    if cost >= 0:
        return close_search(space, n + 1, at_most - (at_most - n) // 2, at_most)
    return n


def part1(lines: list[str], size: int = 71, after: int = 1024) -> int:
    from timer import Timer
    with Timer():
        space = Space.from_lines(lines, n=size).first(after)
        return space.cost()


def part2(lines: list[str], size: int = 71, after: int = 1024) -> int:
    from timer import Timer
    with Timer():
        space = Space.from_lines(lines, n=size)
        last = close_search(space, after, after + (len(lines) - after) // 2, len(lines))
        return lines[last]


if __name__ == '__main__':
    from faoci.interface import fetch_lines

    assert part1(load_lines('y24d18'), 7, 12) == 22
    assert part2(load_lines('y24d18'), 7, 12) == '6,1'

    puzzle = fetch_lines(year=2024, day=18)
    print(f'Part 1: {part1(puzzle)}')
    print(f'Part 2: {part2(puzzle)}')
