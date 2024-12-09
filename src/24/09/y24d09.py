# Path: /home/g/Code/advent-of-python/src/24/09/y24d09.py
# Puzzle Source: https://adventofcode.com/2024/day/9
from dataclasses import dataclass, field
from typing import TypeVar

def load_txt_lines(named: str):
    from pathlib import Path
    with Path(__file__).parent.joinpath(f'{named}.txt').open('r') as f:
        lines = f.read().split('\n')
    return lines[:-1] if len(lines[-1]) == 0 else lines


@dataclass(order=True)
class File:
    pos: int
    num: int = field(compare=False)
    fid: int = field(compare=False)

    def checksum(self):
        return sum((self.pos + i)*self.fid for i in range(self.num))


@dataclass
class FileSystem:
    files: list[File]

    def __str__(self):
        N = max(self.files)
        chrs = ['.' for _ in range(N.pos + N.num)]
        for f in self.files:
            for i in range(f.pos, f.pos+f.num):
                chrs[i] = hex(f.fid)[-1]
        return ''.join(chrs)

    def fit(self, earliest: int = 0, latest: int = -1, space: int = 1):
        p = earliest
        l = max(self.files).pos if latest < 0 else latest
        for file in self.files:
            if file.pos > p and (file.pos - p) >= space:
                return File(p, file.pos - p, -1)
            p = file.pos + file.num
            if p > l:
                break
        return File(p, 0, -1)

    def move_last(self):
        last = max(self.files)
        free = self.fit(earliest=0, space=1)
        if free.pos >= last.pos:
            # no free space to move into
            return False
        
        if free.num < last.num:
            split = File(last.pos, last.num - free.num, last.fid)
            self.files.append(split)
            last.num = free.num
        last.pos = free.pos
        self.files = sorted(self.files)
        return True

    def compact(self):
        moves = 0
        while self.move_last():
            moves += 1
        return moves

    def defrag(self):
        moves = 0
        self.files = sorted(self.files)
        check_from = self.files[0].num
        for f in reversed(self.files):
            free = self.fit(earliest=check_from, latest=f.pos, space=f.num)
            if free.pos < f.pos:
                f.pos = free.pos
                check_from = f.pos + f.num
                moves += 1
                self.files = sorted(self.files)
        return moves

    def checksum(self):
        return sum(file.checksum() for file in self.files)

    @classmethod
    def from_map(cls, sizes: str):
        files = []
        pos = 0
        for i in range(len(sizes)):
            n = int(sizes[i])
            if i % 2 == 0:
                files.append(File(pos, n, i // 2))
            pos += n
        return cls(files)


def part1(lines: list[str]) -> int:
    fs = FileSystem.from_map(lines[0])
    steps = fs.compact()
    print(f'Compacted in {steps=}')
    return fs.checksum()


def part2(lines: list[str]) -> int:
    fs = FileSystem.from_map(lines[0])
    steps = fs.defrag()
    print(f'Defraged in {steps=}')
    return fs.checksum()


if __name__ == '__main__':
    from faoci.interface import fetch_lines
    from timer import Timer

    assert part1(load_txt_lines('example')) == 1928
    assert part2(load_txt_lines('example')) == 2858

    with Timer(text="Part 1: elapsed time {:0.2f} s") as t:
        print(f'\tPart 1: {part1(fetch_lines(year=2024, day=9))}')
    with Timer(text="Part 2: elapsed time {:0.2f} s") as t:
        print(f'\tPart 2: {part2(fetch_lines(year=2024, day=9))}')
