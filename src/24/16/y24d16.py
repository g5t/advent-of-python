# Path: /home/g/Code/advent-of-python/src/24/16/y24d16.py
# Puzzle Source: https://adventofcode.com/2024/day/16
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

    def turns(self, d):
        if self.x == d.x and self.y == d.y:
            return 0
        if abs(self.x) == abs(d.y) and abs(self.y) == abs(d.x):
            return 1
        if abs(self.x) == abs(d.x) and abs(self.y) == abs(d.y):
            return 2
        return -100




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
class Maze:
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
    def from_lines(cls, lines: list[str]):
        from itertools import product
        nx = len(lines[0])
        assert all(len(line) == nx for line in lines)
        bm = [[0 for _ in line] for line in lines]
        start, goal = None, None
        for x, y in product(range(nx), range(len(bm))):
            if lines[y][x] == '#':
                bm[y][x] = 1
            elif lines[y][x] == 'E':
                goal = Point(x, y)
            elif lines[y][x] == 'S':
                start = Point(x, y)
        return cls(tuple(tuple(row) for row in bm), start, goal)

    def dirs(self):
        return Point(0, 1), Point(1, 0), Point(0, -1), Point(-1, 0)

    def char_map(self):
        return [['#' if x else '.' for x in row] for row in self.bitmap]

    def spaces(self):
        from itertools import product
        return [Point(x, y) for x, y in product(range(self.nx), range(self.ny)) if self.bitmap[y][x] == 0]

    def ways(self, p: Point, d: Point):
        l, r = Point(abs(d.y), abs(d.x)), Point(-abs(d.y), -abs(d.x))
        n_d_c = [(p, l, 1000), (p, r, 1000)]
        n = p + d
        if 0 <= n.x < self.nx and 0 <= n.y < self.ny and self.at(n) == 0:
            n_d_c.append((n, d, 1))
        return n_d_c

    def build_graphs(self):
        from itertools import product
        for p, d in product(self.spaces(), self.dirs()):
            fkey = p, d
            for n, d, c in self.ways(p, d):
                self.forward.setdefault(fkey, {})[(n, d)] = c
                self.reverse.setdefault((n ,d), {})[fkey] = c

        gkey = self.goal, Point(0, 0)
        for d in self.dirs():
            self.forward.setdefault((self.goal, d), {})[gkey] = 0
            self.reverse.setdefault(gkey, {})[(self.goal, d)] = 0
    
    def __post_init__(self):
        self.build_graphs()

    def djikstra(self, start: tuple[Point, Point], graph: dict[tuple[Point, Point], dict[tuple[Point, Point], 1]]):
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
        distances = self.djikstra((self.start, Point(1, 0)), self.forward)
        return distances.get((self.goal, Point(0, 0)), -1), distances

    def seats(self, fwd=None):
        gkey = self.goal, Point(0, 0)
        fwd = fwd or self.djikstra((self.start, Point(1, 0)), self.forward)
        rev = self.djikstra(gkey, self.reverse)
        best = set()
        for key, cost in fwd.items():
            if key != gkey and cost + rev.get(key, 2*fwd[gkey]) == fwd[gkey]:
                best.add(key[0])
        return len(best)


def parts(lines: list[str]) -> int:
    from timer import Timer
    with Timer():
        maze = Maze.from_lines(lines)
        cost, fwd = maze.cost()
        return cost, maze.seats(fwd)


if __name__ == '__main__':
    from faoci.interface import fetch_lines

    assert parts(load_lines('y24d16a')) == (7036, 45)
    assert parts(load_lines('y24d16b')) == (11048, 64)

    puzzle = fetch_lines(year=2024, day=16)
    part1, part2 = parts(puzzle)
    print(f'Part 1: {part1}')
    print(f'Part 2: {part2}')
