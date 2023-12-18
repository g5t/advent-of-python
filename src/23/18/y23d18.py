# Path: /home/gst/PycharmProjects/aoc23/src/23/18/y23d18.py
# Puzzle Source: https://adventofcode.com/2023/day/18
from dataclasses import dataclass


@dataclass
class PolyHole:
    _vertices: tuple[tuple[int, int], ...]
    _edges: tuple[tuple[int, int], ...]

    def minimum(self):
        return min(v[0] for v in self._vertices), min(v[1] for v in self._vertices)

    def maximum(self):
        return max(v[0] for v in self._vertices), max(v[1] for v in self._vertices)

    def ground_array(self):
        min_yx = self.minimum()
        max_yx = self.maximum()
        ground = [['.' for _ in range(min_yx[1], max_yx[1] + 1)] for _ in range(min_yx[0], max_yx[0] + 1)]
        for edge in self._edges:
            v0 = self._vertices[edge[0]]
            v1 = self._vertices[edge[1]]
            d = [min(max(x, -1), 1) for x in (v1[0] - v0[0], v1[1] - v0[1])]
            while v0 != v1:
                if v0[0] < min_yx[0] or v0[1] < min_yx[1] or v0[0] > max_yx[0] or v0[1] > max_yx[1]:
                    raise RuntimeError('Out of bounds array indexing')
                ground[v0[0] - min_yx[0]][v0[1] - min_yx[1]] = '#'
                v0 = v0[0] + d[0], v0[1] + d[1]
        return ground

    def __str__(self):
        return '\n'.join(''.join(row) for row in self.ground_array())

    def perimeter(self):
        p = 0
        for edge in self._edges:
            v0 = self._vertices[edge[0]]
            v1 = self._vertices[edge[1]]
            p += abs(v1[0] - v0[0]) + abs(v1[1] - v0[1])
        return p

    @classmethod
    def from_plans(cls, plans: list[str]):
        v = [(0, 0)]
        for instruction in plans:
            dir_char, distance, color = instruction.split(' ')
            distance = int(distance)
            if 'R' == dir_char:
                vector = (0, distance)
            elif 'D' == dir_char:
                vector = (distance, 0)
            elif 'U' == dir_char:
                vector = (-distance, 0)
            elif 'L' == dir_char:
                vector = (0, -distance)
            else:
                raise ValueError(f'Unexpected direction character {dir_char}')
            v.append((v[-1][0] + vector[0], v[-1][1] + vector[1]))
        return PolyHole.from_vertices(tuple(v))

    @classmethod
    def from_colors(cls, plans: list[str]):
        v = [(0, 0)]
        for instruction in plans:
            color = instruction.split(' ')[-1].strip('(#)')
            distance, dir_int = int(color[:5], base=16), color[-1]
            if '0' == dir_int:
                vector = (0, distance)
            elif '1' == dir_int:
                vector = (distance, 0)
            elif '2' == dir_int:
                vector = (0, -distance)
            elif '3' == dir_int:
                vector = (-distance, 0)
            else:
                raise ValueError(f'Unexpected direction int {dir_int}')
            v.append((v[-1][0] + vector[0], v[-1][1] + vector[1]))
        return PolyHole.from_vertices(tuple(v))

    @classmethod
    def from_vertices(cls, vertices: tuple[tuple[int, int], ...]):
        if vertices[0] == vertices[-1]:
            vertices = vertices[:-1]
        return PolyHole(vertices, tuple([(i, (i + 1) % len(vertices)) for i in range(len(vertices))]))

    def area(self):
        """Find the area of the polygon plus its border:
        The 'inner' area is calculated using Green's theorem, and then we rely on a Minkowski sum of that area
        and the 'border' area -- thanks to Redditor `ricbit` for providing a useful explanation of the same
        equation that _could_ be used on day 10:
            https://old.reddit.com/r/adventofcode/comments/18l0qtr/2023_day_18_solutions/kdv8oai/
        """
        # We can use Green's theorem for a vector field with constant partial-derivative differences
        # dFy/dx - dFx/dy = 1, e.g., F = (Fx, Fy) = Fx xhat + Fy yhat == (-y/2, x/2)
        # Then the area is the integral of F . ds around the boundary
        vs = [(self._vertices[a], self._vertices[b]) for a, b in self._edges]
        # calculate 4*Area by leaving off the division by 2 for F and for the midpoint of each line segment
        four = [(a[0] + b[0]) * (a[1] - b[1]) - (a[1] + b[1]) * (a[0] - b[0]) for a, b in vs]
        # We also must account for the area of the boundary, which works out to perimeter/2 + area('brush')
        return sum(four) // 4 + self.perimeter()//2 + 1


def get_lines(filename):
    from pathlib import Path
    if isinstance(filename, str):
        filename = Path(filename)
    filename = filename.resolve()
    if not filename.exists():
        return []

    with open(filename, 'r') as file:
        return file.read().splitlines()


def part1(lines: list[str]) -> int:
    hole = PolyHole.from_plans(lines)
    return hole.area()


def part2(lines: list[str]) -> int:
    hole = PolyHole.from_colors(lines)
    return hole.area()


if __name__ == '__main__':
    from faoci.interface import fetch_lines

    assert part1(get_lines('y23d18b.test')) == 4
    assert part1(get_lines('y23d18a.test')) == 36
    assert part1(get_lines('y23d18c.test')) == 36
    assert part1(get_lines('y23d18.test')) == 62
    assert part2(get_lines('y23d18.test')) == 952408144115

    puzzle = fetch_lines(year=2023, day=18)
    print(f'Part 1: {part1(puzzle)}')
    print(f'Part 2: {part2(puzzle)}')
