# Path: /home/g/Code/advent-of-python/src/24/19/y24d19.py
# Puzzle Source: https://adventofcode.com/2024/day/19
from dataclasses import dataclass, field
from typing import TypeVar, Any
from functools import cache


def load_lines(named: str):
    from pathlib import Path
    with Path(__file__).parent.joinpath(f'{named}.test').open('r') as f:
        lines = f.read().split('\n')
    return lines[:-1] if len(lines[-1]) == 0 else lines


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
class Supply:
    towels: tuple[str,...]

    def __hash__(self):
        return hash(self.towels)
    
    @classmethod
    def from_line(cls, line: str):
        return cls(tuple(x.strip() for x in line.split(',')))

    def match(self, design: str):
        queue = Heap()
        queue.push(Heap.Item(len(design), (design, tuple())))
        while len(queue):
            work, components = queue.pop().item
            if len(work):
                for t in self.towels:
                    if work.startswith(t):
                        rem = work[len(t):]
                        cmp = components + (t,)
                        queue.push(Heap.Item(len(rem), (rem, cmp)))
            else:
                return 1
        return 0

    @cache
    def count(self, design: str):
        return sum(self.count(design[len(t):]) for t in self.towels if design.startswith(t)) if len(design) else 1
    

def part1(lines: list[str]) -> int:
    supply = Supply.from_line(lines[0])
    return sum(1 for design in lines[2:] if supply.match(design))


def part2(lines: list[str]) -> int:
    supply = Supply.from_line(lines[0])
    return sum(supply.count(design) for design in lines[2:])


if __name__ == '__main__':
    from faoci.interface import fetch_lines

    assert part1(load_lines('y24d19')) == 6

    puzzle = fetch_lines(year=2024, day=19)
    print(f'Part 1: {part1(puzzle)}')
    print(f'Part 2: {part2(puzzle)}')
