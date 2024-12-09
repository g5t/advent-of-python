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

    @property
    def end(self):
        return self.pos + self.num


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


    def compact(self):
        from collections import deque
        moves = 0
        fs = deque(sorted(self.files))
        back = fs[-1]
        check_from = 0
        while check_from + 1 < len(fs):
            last_end = fs[check_from].end
            back = fs.pop()
            p = check_from + 1
            while p < len(fs) and fs[p].pos == last_end:
                last_end = fs[p].end
                p += 1
            if p < len(fs):
                if (free := fs[p].pos - last_end) < back.num:
                    fs.append(File(back.pos, back.num - free, back.fid))
                    back.num = free
            back.pos = last_end
            fs.insert(p, back)
            check_from = p
            moves += 1
                
        self.files = list(fs)
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

    with Timer(text="\telapsed time {:0.2f} s") as t:
        print(f'Part 1: {part1(fetch_lines(year=2024, day=9))}')
    with Timer(text="\telapsed time {:0.2f} s") as t:
        print(f'Part 2: {part2(fetch_lines(year=2024, day=9))}')
