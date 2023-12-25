# Path: /home/gst/PycharmProjects/aoc23/src/23/24/y23d24.py
# Puzzle Source: https://adventofcode.com/2023/day/24
from __future__ import annotations
from dataclasses import dataclass


def dot(a, b):
    return sum(i*j for i, j in zip(a, b))


def norm(a):
    from math import sqrt
    return sqrt(dot(a, a))


@dataclass
class HailRay:
    x: int
    y: int
    z: int
    vx: int
    vy: int
    vz: int

    def __str__(self):
        return f'{self.x}, {self.y}, {self.z} @ {self.vx}, {self.vy}, {self.vz}'

    @classmethod
    def from_string(cls, string: str):
        pos, vec = string.split(' @ ')
        x, y, z = [int(x) for x in pos.split(',')]
        vx, vy, vz = [int(x) for x in vec.split(',')]
        return cls(x, y, z, vx, vy, vz)

    def __sub__(self, other):
        return HailRay(self.x - other.x, self.y - other.y, self.z - other.z,
                       self.vx - other.vx, self.vy - other.vy, self.vz - other.vz)

    @property
    def v(self):
        return self.vx, self.vy, self.vz

    @property
    def v_xy(self):
        return self.vx, self.vy

    def intersects_xy(self, other):
        if dot(self.v_xy, other.v_xy) == norm(self.v_xy) * norm(other.v_xy):
            print(f'Rays {self} and {other} do not intersect')
            return False
        return True

    def paths_cross_xy_future_area(self, other, x_lims: tuple[int, int], y_lims: tuple[int, int]):
        if not self.intersects_xy(other):
            return False
        a_m = self.vy / self.vx
        b_m = other.vy / other.vx
        a_b = self.y - a_m * self.x
        b_b = other.y - b_m * other.x
        if a_m != b_m:
            x = (b_b - a_b) / (a_m - b_m)
            y = a_m * x + a_b
            a_t = (x - self.x) / self.vx
            b_t = (x - other.x) / other.vx
            if a_t > 0 and b_t > 0 and x_lims[0] <= x <= x_lims[1] and y_lims[0] <= y <= y_lims[1]:
                return True
        elif a_b == b_b:
            return True
        return False


@dataclass
class Hail:
    rays: tuple[HailRay, ...]

    @classmethod
    def from_lines(cls, lines: list[str]):
        return cls(tuple(HailRay.from_string(line) for line in lines))

    def intersection_xy_count(self, x_lims: tuple[int, int] | None = None, y_lims: tuple[int, int] | None = None):
        if x_lims is None:
            x_lims = (200000000000000, 400000000000000)
        if y_lims is None:
            y_lims = (200000000000000, 400000000000000)
        count = 0
        for i in range(len(self.rays) - 1):
            for j in range(i+1, len(self.rays)):
                if self.rays[i].paths_cross_xy_future_area(self.rays[j], x_lims, y_lims):
                    count += 1
        return count

    def hit_them_all(self):
        vxs, vys, vzs = None, None, None

        def merge_guesses(a, b, va, guess):
            new = [v for v in range(-1000, 1000) if v != va and (b - a) % (v - va) == 0]
            if guess is None:
                return set(new)
            return guess & set(new)

        for i in range(len(self.rays) - 1):
            for j in range(i+1, len(self.rays)):
                if self.rays[i].vx == self.rays[j].vx and abs(self.rays[i].vx) > 100:
                    vxs = merge_guesses(self.rays[i].x, self.rays[j].x, self.rays[i].vx, vxs)
                if self.rays[i].vy == self.rays[j].vy and abs(self.rays[i].vy) > 100:
                    vys = merge_guesses(self.rays[i].y, self.rays[j].y, self.rays[i].vy, vys)
                if self.rays[i].vz == self.rays[j].vz and abs(self.rays[i].vz) > 100:
                    vzs = merge_guesses(self.rays[i].z, self.rays[j].z, self.rays[i].vz, vzs)

        # We probably have a single option for the rock velocity vector, but might not
        if len(vxs) * len(vys) * len(vzs) > 1:
            print(f'vx is one of {vxs}\nvy is one of {vys}\nvz is one of {vzs}')

        vx, vy, vz = vxs.pop(), vys.pop(), vzs.pop()
        a, b = self.rays[0], self.rays[1]
        m_a = (a.vy - vy) / (a.vx - vx)
        m_b = (b.vy - vy) / (b.vx - vx)
        b_a = a.y - m_a * a.x
        b_b = b.y - m_b * b.x
        x = int((b_b - b_a) / (m_a - m_b))
        y = int(m_a * x + b_a)
        t = (x - a.x) // (a.vx - vx)
        z = a.z + (a.vz - vz) * t
        return HailRay(x, y, z, vx, vy, vz)


def part1(lines: list[str]) -> int:
    hail = Hail.from_lines(lines)
    return hail.intersection_xy_count()


def part2(lines: list[str]) -> int:
    hail = Hail.from_lines(lines)
    rock = hail.hit_them_all()
    return rock.x + rock.y + rock.z


if __name__ == '__main__':
    from faoci.interface import fetch_lines

    def get_lines(filename):
        from pathlib import Path
        if isinstance(filename, str):
            filename = Path(filename)
        filename = filename.resolve()
        if not filename.exists():
            return []
        with open(filename, 'r') as file:
            return file.read().splitlines()

    test_hail = Hail.from_lines(get_lines('y23d24.test'))
    assert test_hail.intersection_xy_count((7, 27), (7, 27)) == 2

    puzzle = fetch_lines(year=2023, day=24)
    print(f'Part 1: {part1(puzzle)}')
    print(f'Part 2: {part2(puzzle)}')
