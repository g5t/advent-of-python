# Path: /home/g/Code/advent-of-python/src/24/07/y24d07.py
# Puzzle Source: https://adventofcode.com/2024/day/7
from dataclasses import dataclass, field
from typing import TypeVar

def example():
    from pathlib import Path
    with Path(__file__).parent.joinpath('example.txt').open('r') as f:
        lines = f.read().split('\n')
    return lines[:-1] if len(lines[-1]) == 0 else lines

TQ = TypeVar('TQ', bound='Q')

@dataclass
class Q:
    goal: int
    values: tuple[int,...] = field(default_factory=tuple)
    parent: tuple[TQ, chr] | None = None

    def __str__(self):
        s = f'({self.parent[1]}) ' if self.parent else ''
        return f'{s}{self.goal}: {self.values}'

    def __hash__(self):
        return hash((self.goal,)+self.values)

    def passed(self):
        # The test passes if and only if it reduces 
        # the goal value to the last input value
        return len(self.values) == 1 and self.goal == self.values[0]

    def overshot(self):
        return self.goal > 1 and len(self.values) and self.goal < self.values[0]

    def options(self):
        g, v0, vs = self.goal, self.values[-1], self.values[:-1]
        # Only addition or subtraction are allowed (for part 1)
        ops = (('+', g - v0, True, vs), ('*', g // v0, g % v0 == 0, vs))
        return ops
        
    @classmethod
    def new(cls, goal, values, parent):
        return cls(goal, values, parent)

    def step(self) -> list[TQ]:
        if len(self.values) == 0:
            return []
        return [o for o in [self.new(g, vs, (self, k)) for k, g, ok, vs in self.options() if ok] if not o.overshot()]

    @classmethod
    def from_str(cls, s: str):
        goal, values = s.split(':', 1)
        values = [int(x) for x in values.split()]
        return cls(int(goal), tuple(values))


class Q2(Q):
    def options(self):
        # part 2 adds the concatenation operator, which is a bit tricker in reverse
        opts = super().options()
        g, vs, v = self.goal, self.values[:-1], self.values[-1]
        if g > 0 and str(g).endswith(str(v)):
            gs = str(g)[:-len(str(v))]
            g = int(gs) if len(gs) else 0
            opts += (('|', g, True, vs),)
        return opts


def solveQ(q: Q):
    from queue import SimpleQueue
    solutions = set()
    queue = SimpleQueue()

    def put_if(ql: list[Q]):
        for x in ql:
            if x.passed():
                solutions.add(x)
            else:
                queue.put(x)

    put_if(q.step())
    while queue.qsize():
        q = queue.get()
        put_if(q.step())

    return len(solutions)


def part1(lines: list[str]) -> int:
    qs = [Q.from_str(line) for line in lines]
    return sum(q.goal for q in qs if solveQ(q))


def part2(lines: list[str]) -> int:
    qs = [Q2.from_str(line) for line in lines]
    return sum(q.goal for q in qs if solveQ(q))


if __name__ == '__main__':
    from faoci.interface import fetch_lines

    assert part1(example()) == 3749
    assert part2(example()) == 11387

    print(f'Part 1: {part1(fetch_lines(year=2024, day=7))}')
    print(f'Part 2: {part2(fetch_lines(year=2024, day=7))}')
