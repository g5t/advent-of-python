# Path: /home/g/Code/advent-of-python/src/24/06/y24d06.py
# Puzzle Source: https://adventofcode.com/2024/day/6
from dataclasses import dataclass

def example():
    from pathlib import Path
    with Path(__file__).parent.joinpath('example.txt').open('r') as f:
        lines = f.read().split('\n')
    return lines[:-1] if len(lines[-1]) == 0 else lines

@dataclass
class P:
    x: int
    y: int
    def __add__(self, other):
        return D(self.x + other.x, self.y + other.y)
    def __sub__(self, other):
        return D(self.x - other.x, self.y - other.y)
    def __str__(self):
        return f'P({self.x}, {self.y})'
    def __hash__(self):
        return hash((self.x, self.y))

class D(P):
    def __str__(self):
        n, e, s, w = D(0, -1), D(1, 0), D(0, 1), D(-1, 0)
        chrs = {n: '^', e: '>', s: 'v', w: '<'}
        return chrs.get(self, '!')

    @classmethod
    def from_chr(cls, o: chr):
        n, e, s, w = D(0, -1), D(1, 0), D(0, 1), D(-1, 0)
        chrs = {'^': n, '>': e, 'v': s, '<': w}
        if o in chrs:
            return chrs[o]
        raise RuntimeError(f"Orientation not found for {o}")

    def next(self):
        n, e, s, w = D(0, -1), D(1, 0), D(0, 1), D(-1, 0)
        nchr = {n: e, e: s, s: w, w: n}
        if self in nchr:
            return nchr[self]
        raise RuntimeError("No next orientation")



class B:
    def __init__(self, board: list[list[int]], position: P, orientation: D):
        self.board = board
        self.position = position
        self.orientation = orientation
        self.history = {}

    @classmethod
    def from_lines(cls, lines: list[str]):
        board = []
        pos, ori = None, None
        for line in lines:
            y = len(board)
            board.append([])
            for x, c in enumerate(line):
                board[-1].append(-1 if '#' == c else 0)
                if c in ('^', '>', 'v', '<'):
                    pos = P(x, y)
        if pos is None:
            raise RuntimeError("Starting point not found")
        return cls(board, pos, D.from_chr(lines[pos.y][pos.x]))

    def __str__(self):
        def c(x):
            if x > 0:
                return str(hex(x % 16))[-1]
            return '#' if x < 0 else '.'
        chrs = [[c(b) for b in rows] for rows in self.board]
        chrs[self.position.y][self.position.x] = str(self.orientation)
        return '\n'.join(''.join(row) for row in chrs)

    def step(self) -> int:
        stepped = False
        d = self.orientation
        while not stepped:
            npos = self.position + d
            # out of bounds -> done
            if npos.y < 0 or npos.y >= len(self.board) or npos.x < 0 or npos.x >= len(self.board[npos.y]):
                self.board[self.position.y][self.position.x] += 1
                return 0
            if self.board[npos.y][npos.x] < 0:
                # no step
                d = d.next()
                if d == self.orientation:
                   raise RuntimeError("Revolved on the spot!")
            else:
                self.board[self.position.y][self.position.x] += 1
                self.position = npos
                self.orientation = d
                if self.position not in self.history:
                    self.history[self.position] = set()
                if d in self.history[self.position]:
                    # print(f'{self}\n')
                    return -1
                self.history[self.position].add(d)
                stepped = True
        return 1 if stepped else 0

    def walk(self):
        steps = 0
        while self.step():
            steps += 1
        return steps

    def has_loop(self):
        last = self.step()
        while last > 0:
            last = self.step()
        return last < 0

    def visit_count(self):
        return sum(sum(x > 0 for x in row) for row in self.board)

    def empty_spots(self) -> set[P]:
        return {P(x, y) for y, r in enumerate(self.board) for x, v in enumerate(r) if v == 0}

    def visited(self) -> set[P]:
        return {P(x, y) for y, r in enumerate(self.board) for x, v in enumerate(r) if v > 0}



def part1(lines: list[str]) -> int:
    b = B.from_lines(lines)
    b.walk()
    return b.visit_count()


def part2(lines: list[str]) -> int:
    b0 = B.from_lines(lines)
    options = []
    all_empty = b0.empty_spots()
    b0.walk()
    visited = b0.visited()
    to_check = all_empty.intersection(visited)
    for opt in to_check:
        bt = B.from_lines(lines)
        # insert an obstacle
        bt.board[opt.y][opt.x] = -1
        if bt.has_loop():
            options.append(opt)
    return len(options)


if __name__ == '__main__':
    from faoci.interface import fetch_lines
    from timer import Timer

    assert part1(example()) == 41
    assert part2(example()) == 6

    with Timer(text="Part 1: elapsed time {:0.2f} s") as t:
        print(f'Part 1: {part1(fetch_lines(year=2024, day=6))}')
    with Timer(text="Part 2: elapsed time {:0.2f} s") as t:
        print(f'Part 2: {part2(fetch_lines(year=2024, day=6))}')
