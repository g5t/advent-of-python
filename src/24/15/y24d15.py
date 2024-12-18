# Path: /home/g/Code/advent-of-python/src/24/15/y24d15.py
# Puzzle Source: https://adventofcode.com/2024/day/15
from dataclasses import dataclass, field
from typing import TypeVar
 

@dataclass
class Point:
    x: int
    y: int

    def __hash__(self):
        return hash((self.x, self.y))

    def __add__(self, other):
        if isinstance(other, Point):
            return Point(self.x + other.x, self.y + other.y)
        return Point(self.x + other, self.y + other)

    def __sub__(self, other):
        if isinstance(other, Point):
            return Point(self.x - other.x, self.y - other.y)
        return Point(self.x - other, self.y - other)

    def __mul__(self, other):
        if isinstance(other, Point):
            return self.x * other.x + self.y * other.y
        return Point(self.x * other, self.y * other)
    
    def __floordiv__(self, other):
        if isinstance(other, Point):
            return Point(self.x // other.x, self.y // other.y)
        return Point(self.x // other, self.y // other)

    def __rmul__(self, other):
        return Point(other * self.x, other * self.y)

    def __mod__(self, other):
        if isinstance(other, Point):
            return Point(self.x % other.x, self.y % other.y)
        return Point(self.x % other, self.y % other)

    def __str__(self):
        return f'({self.x}, {self.y})'
    
    def __repr__(self):
        return str(self)

    @classmethod
    def from_str(cls, s: str):
        return cls(*[int(x) for x in s.split(',')])

    @classmethod
    def from_chr(cls, c: chr):
        return {'<': Point(-1, 0), '^': Point(0, -1), '>': Point(1, 0), 'v': Point(0, 1)}[c]



TBox = TypeVar('TBox', bound='Box')
@dataclass
class Box:
    """A box that can be more than one square
    The support dictionary holds references to any boxes that
    would prevent this box from moving in any given direction.
    """
    chars: str
    position: tuple[Point, ...]

    def __hash__(self):
        return hash(self.position)

    def __str__(self):
        d = {k: len(v) for k, v in self.support.items()}
        return f'{self.chars}{self.position}{d}'

    def __repr__(self):
        return f'Box({self})'

    def __add__(self, other):
        return Box(self.chars, tuple(x + other for x in self.position))

    def push(self, direction: Point):
        self.position = tuple(x + direction for x in self.position)
        return self

    def gps(self):
        p = self.position[0]
        return 100 * p.y + p.x

    def chr_pos_iter(self):
        return zip(self.chars, self.position)

    def touches(self, direction: Point, other: TBox):
        """If this box moved in the specified direction, would it overlap with the other box?"""
        from itertools import product
        return any(x + direction == y for x, y in product(self.position, other.position))


@dataclass
class Warehouse:
    shape: tuple[int, int]
    walls: tuple[Point, ...]
    boxes: tuple[Box, ...]

    def gps(self):
        return sum(p.gps() for p in self.boxes)

    def __hash__(self):
        return hash(gps)

    def chr_map(self):
        b = [['.' for x in range(self.shape[0])] for y in range(self.shape[1])]
        for w in self.walls:
            b[w.y][w.x] = '#'
        for c, p in [z for box in self.boxes for z in box.chr_pos_iter()]:
            b[p.y][p.x] = c
        return b

    def push(self, at: Box, d: Point):
        pos = at.position[0] + d
        if pos in self.walls:
            return at

        moved = set()

        def move(collided):
            n = collided + d
            if any(x in self.walls for x in n.position):
                return False
            for box in [b for b in self.boxes if b != collided and collided.touches(d, b)]:
                if move(box):
                    moved.add(box)
                else:
                    return False
            return True

        collided = next((box for box in self.boxes if any(x == pos for x in box.position)), None,)
        if collided is not None:
            if move(collided):
                for movement in moved:
                    movement.push(d)
                collided.push(d)
                return at.push(d)
        else:
            return at.push(d)
        return at


@dataclass
class Robot:
    at: Box
    warehouse: Warehouse
    instructions: str

    @classmethod
    def from_lines(cls, lines: list[str], part: int = 1):
        split = next(iter(i for i, line in enumerate(lines) if len(line) == 0))
        walls, boxes, position = [], [], Point(-1, -1)
        shape = part * len(lines[0]), split
        for y, line in enumerate(lines[:split]):
            for x, c in enumerate(line):
                points = [Point(part * x, y), Point(part * x + 1, y)]
                if '#' == c:
                    if part == 1:
                        walls.append(points[0])
                    else:
                        walls.extend(points)
                elif 'O' == c:
                    if part == 1:
                        box = Box('O', (points[0],))
                    else:
                        box = Box('[]', tuple(points))
                    boxes.append(box)
                elif '@' == c:
                    position = points[0]

        warehouse = Warehouse(shape, walls, boxes)
        instructions = ''.join(lines[split:])
        at = Box('@', (position,))
        return cls(at, warehouse, instructions)

    def __str__(self):
        b = self.warehouse.chr_map()
        for c, p in self.at.chr_pos_iter():
            b[p.y][p.x] = c
        return '\n'.join(''.join(row) for row in b)

    def run(self):
        for instruction in self.instructions:
            self.at = self.warehouse.push(self.at, Point.from_chr(instruction))
        return self


def get_lines(filename):
    from pathlib import Path
    if isinstance(filename, str):
        filename = Path(filename)
    filename = filename.resolve()
    if not filename.exists():
        return []

    with open(filename, 'r') as file:
        return file.read().splitlines()


def solve(lines: list[str], part: int=1) -> int:
    return Robot.from_lines(lines, part=part).run().warehouse.gps()


if __name__ == '__main__':
    from faoci.interface import fetch_lines
    from pathlib import Path

    puzzle = fetch_lines(year=2024, day=15)
    print(f'Part 1: {solve(puzzle)}')
    print(f'Part 2: {solve(puzzle, 2)}')
