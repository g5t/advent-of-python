# Path: /home/g/Code/advent-of-python/src/24/11/y24d11.py
# Puzzle Source: https://adventofcode.com/2024/day/11
from dataclasses import dataclass, field
from typing import TypeVar

@dataclass
class S:
    value: int

    def __hash__(self):
        return hash(self.value)

    def __str__(self):
        return str(self.value)

    def __repr__(self):
        return str(self)

    def blink(self):
        from math import log10, ceil
        if self.value == 0:
            return [S(1)]
        if (d := ceil(log10(self.value + 1))) > 0 and d  % 2 == 0:
            p = 10 ** (int(d) / 2)
            return [S(int(self.value // p)), S(int(self.value % p))]
        return [S(self.value * 2024)]


def part1(lines: list[str]) -> int:
    stones = [S(int(x)) for x in lines[0].split()]
    return n_blinks(stones, 25)


def part2(lines: list[str]) -> int:
    stones = [S(int(x)) for x in lines[0].split()]
    return n_blinks(stones, 75)


def memo(f):
    knowledge = dict()
    def inner(stone: S, count: int):
        if (stone, count) not in knowledge:
            knowledge[(stone, count)] = f(stone, count)
        return knowledge[(stone, count)]
    return inner


@memo
def follow(stone: S, count: int):
    if count == 0:
        return 1
    return sum(follow(s, count - 1) for s in stone.blink())


def n_blinks(stones: list[S], count: int):
    return sum(follow(stone, count) for stone in stones)


if __name__ == '__main__':
    from faoci.interface import fetch_lines
    from timer import Timer

    assert n_blinks([S(125), S(17)], 6) == 22
    assert n_blinks([S(125), S(17)], 25) == 55312

    with Timer(text="\telapsed time {:0.2f} s") as t:
        print(f'Part 1: {part1(fetch_lines(year=2024, day=11))}')

    with Timer(text="\telapsed time {:0.2f} s") as t:
        print(f'Part 2: {part2(fetch_lines(year=2024, day=11))}')
