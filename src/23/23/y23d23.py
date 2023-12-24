# Path: /home/gst/PycharmProjects/aoc23/src/23/23/y23d23.py
# Puzzle Source: https://adventofcode.com/2023/day/23
from __future__ import annotations

from dataclasses import dataclass, field


def options(key: list[str], rows: int, cols: int, x: int, y: int, allowed: tuple[str, str, str, str]):
    opts = []
    if 0 <= x - 1 < rows and 0 <= y <= cols and key[x - 1][y] in allowed[0]:
        opts.append((x - 1, y))
    if 0 <= x + 1 < rows and 0 <= y <= cols and key[x + 1][y] in allowed[1]:
        opts.append((x + 1, y))
    if 0 <= x < rows and 0 <= y - 1 <= cols and key[x][y - 1] in allowed[2]:
        opts.append((x, y - 1))
    if 0 <= x < rows and 0 <= y + 1 <= cols and key[x][y + 1] in allowed[3]:
        opts.append((x, y + 1))
    return opts


def option_p0(key: list[str], rows: int, cols: int, x: int, y: int, allowed: str):
    if not (0 <= x + 1 < rows and 0 <= y < cols) or key[x + 1][y] not in allowed:
        return None
    n = 1
    while 0 <= x + n + 1 < rows and key[x + n + 1][y] in allowed:
        n += 1
    return x + n, y, n


def option_m0(key: list[str], rows: int, cols: int, x: int, y: int, allowed: str):
    if not (0 <= x - 1 < rows and 0 <= y < cols) or key[x - 1][y] not in allowed:
        return None
    n = 1
    while 0 <= x - n - 1 < rows and key[x - n - 1][y] in allowed:
        n += 1
    return x - n, y, n


def option_0p(key: list[str], rows: int, cols: int, x: int, y: int, allowed: str):
    if not (0 <= x < rows and 0 <= y + 1 < cols) or key[x][y + 1] not in allowed:
        return None
    n = 1
    while 0 <= y + n + 1 < cols and key[x][y + n + 1] in allowed:
        n += 1
    return x, y + n, n


def option_0m(key: list[str], rows: int, cols: int, x: int, y: int, allowed: str):
    if not (0 <= x < rows and 0 <= y - 1 < cols) or key[x][y - 1] not in allowed:
        return None
    n = 1
    while 0 <= y - n - 1 < cols and key[x][y - n - 1] in allowed:
        n += 1
    return x, y - n, n


def extended_options(lines: list[str], rows: int, cols: int, i: int, j: int, spots: str):
    opts = []
    if (pz := option_p0(lines, rows, cols, i, j, spots)) is not None:
        opts.append(pz)
    if (mz := option_m0(lines, rows, cols, i, j, spots)) is not None:
        opts.append(mz)
    if (zp := option_0p(lines, rows, cols, i, j, spots)) is not None:
        opts.append(zp)
    if (zm := option_0m(lines, rows, cols, i, j, spots)) is not None:
        opts.append(zm)
    return opts



def can_skip(lines: list[str], rows: int, cols: int, i: int, j: int, x: int, y: int, spots: str):
    opts = extended_options(lines, rows, cols, x, y, spots)
    if len(opts) == 2:
        other = [opt for opt in opts if opt[0] != i or opt[1] != j]
        if len(other) != 1:
            raise RuntimeError('Unexpected options')
        opt = other[0]
        return x, y, opt[0], opt[1], opt[2]
    return None


@dataclass
class HikingMap:
    _pos_opt: dict[tuple[int, int], list[tuple[int, int, int]]]

    @classmethod
    def from_lines(cls, lines: list[str]):
        from itertools import product
        po = {}
        rows, cols = len(lines), len(lines[0])
        for i, j in product(range(rows), range(cols)):
            opts = []
            if lines[i][j] == '.':
                opts.extend(options(lines, rows, cols, i, j, ('^.', 'v.', '.<', '.>')))
            elif lines[i][j] == '<':
                opts.append((i, j-1))
            elif lines[i][j] == '>':
                opts.append((i, j+1))
            elif lines[i][j] == 'v':
                opts.append((i+1, j))
            elif lines[i][j] == '^':
                opts.append((i-1, j))
            if len(opts):
                po[(i, j)] = [(x, y, 1) for x, y in opts]
        return cls(po)

    def longest_walk(self):
        start = [k for k, v in self._pos_opt.items() if k[0] == 0]
        y_max = max(k[0] for k in self._pos_opt.keys())
        stop = [k for k in self._pos_opt.keys() if k[0] == y_max]
        if len(start) != 1 or len(stop) != 1:
            raise RuntimeError('Non-singular start or stop')
        opts = [(start[0], x, 0, [start[0]]) for x in self._pos_opt[start[0]]]
        routes = []
        distances = []
        while len(opts):
            last, to_step, dist, path = opts.pop(0)
            to = to_step[0], to_step[1]
            if to == stop[0]:
                path.append(to)
                routes.append(path)
                distances.append(dist + to_step[2])
            elif to not in path:
                path.append(to)
                new_opts = self._pos_opt[to]
                opts.extend([(to, x, dist + to_step[2], path.copy()) for x in new_opts if (x[0], x[1]) != last])
        #  return max(len(route) for route in routes) - 1  # don't count the start as part of the path length
        return max(distances)

@dataclass
class HikingNetwork:
    _board: list[list[int, ...], ...]
    _first: tuple[int, int]
    _last: tuple[int, int]
    _nodes: tuple[tuple[int, int], ...] = field(default_factory=tuple)
    _direct: dict[tuple[tuple[int, int], tuple[int, int]], int] = field(default_factory=dict)

    def to_lines(self):
        chars = '#.N'
        return [''.join(chars[x] for x in row) for row in self._board]

    def __str__(self):
        return '\n'.join(self.to_lines())

    def __post_init__(self):
        from itertools import product
        rows, cols = len(self._board), len(self._board[0])
        nodes = []
        print(f'{self}\n')
        for i, j in product(range(rows), range(cols)):
            if len(self.neighbors((i, j))) > 2:
                self._board[i][j] = 2
                nodes.append((i, j))
        self._nodes = tuple(nodes)

        for i, a in enumerate(self._nodes):
            if (df := self.amble(self._first, a)) is not None:
                self._direct[(self._first, a)] = df
            if (dl := self.amble(a, self._last)) is not None:
                self._direct[(a, self._last)] = dl
            for j, b in enumerate(self._nodes):
                if i != j:
                    if (d := self.amble(a, b)) is not None:
                        self._direct[(a, b)] = d

        print(f'{self}\n')
        for ab, d in self._direct.items():
            print(f'{ab[0]}->{ab[1]}: {d}')

    def neighbors(self, a: tuple[int, int]):
        rows, cols = len(self._board), len(self._board[0])
        opts = []
        if self._board[a[0]][a[1]] == 0:
            return opts
        if 0 <= a[0] - 1 < rows and 0 <= a[1] < cols and self._board[a[0] - 1][a[1]] > 0:
            opts.append((a[0] - 1, a[1]))
        if 0 <= a[0] + 1 < rows and 0 <= a[1] < cols and self._board[a[0] + 1][a[1]] > 0:
            opts.append((a[0] + 1, a[1]))
        if 0 <= a[0] < rows and 0 <= a[1] - 1 < cols and self._board[a[0]][a[1] - 1] > 0:
            opts.append((a[0], a[1] - 1))
        if 0 <= a[0] < rows and 0 <= a[1] + 1 < cols and self._board[a[0]][a[1] + 1] > 0:
            opts.append((a[0], a[1] + 1))
        return opts

    def amble(self, a: tuple[int, int], b: tuple[int, int]) -> int | None:
        opts = [(a, x, 0) for x in self.neighbors(a)]
        while len(opts):
            last, to, dist = opts.pop(0)
            if to == b:
                return dist + 1
            # every neighbor is a 1 (non-node) or 2 (node).
            # Any node that is not our destination means there is no direct connection for the amble
            if self._board[to[0]][to[1]] != 2:
                opts.extend((to, x, dist + 1) for x in self.neighbors(to) if x != last)
        return None

    def node_neighbors(self, a: tuple[int, int]):
        opts = set()
        for k in self._direct.keys():
            if k[0] == a:
                opts.add(k[1])
        return list(opts)

    def longest_walk(self):
        # for every node connected to the starting node, etc ...
        states = [(self._first, x, self._direct[(self._first, x)], [self._first]) for x in self.node_neighbors(self._first)]
        dists_paths = []
        longest_to = {}
        while len(states):
            last, to, dist, path = states.pop(0)
            if to == self._last:
                # sorting by length should allow an early return
                dists_paths.append((dist, path))
            elif to not in path and dist > longest_to.get(to, 0):
                print(f'{path=} {to=} {dist=}')
                longest_to[to] = dist
                states.extend((to, x, dist + self._direct[(to, x)], [*path, to]) for x in self.node_neighbors(to) if x != last)
                # sort the possible states by segment length
                states = list(reversed(sorted(states, key=lambda x: x[2])))
        return max(x[0] for x in dists_paths)

    def search(self, node: tuple[int, int] = None, dist: int = 0, best: int = 0, seen: set = set()):
        if node is None:
            node = self._first
        if node == self._last:
            return dist
        if node in seen:
            return best
        seen.add(node)
        best = max(self.search(n, dist + self._direct[(node, n)], best) for n in self.node_neighbors(node))
        seen.remove(node)
        return best

    @classmethod
    def from_lines(cls, lines: list[str]):
        from itertools import product
        rows, cols = len(lines), len(lines[0])
        spots = '.^<>v'
        board = [[0 for _ in range(cols)] for _ in range(rows)]
        for i, j in product(range(rows), range(cols)):
            if lines[i][j] in spots:
                board[i][j] = 1
        first = [j for j, b in enumerate(board[0]) if b]
        last = [j for j, b in enumerate(board[-1]) if b]
        if len(first) != 1 or len(last) != 1:
            raise ValueError('Error finding entrace or exit')

        return cls(board, (0, first[0]), (rows - 1, last[0]))



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
    hike = HikingMap.from_lines(lines)
    return hike.longest_walk()


def part2(lines: list[str]) -> int:
    hike = HikingNetwork.from_lines(lines)
    return hike.search()  # hike.longest_walk()


if __name__ == '__main__':
    from faoci.interface import fetch_lines

    assert part1(get_lines('y23d23.test')) == 94
    assert part2(get_lines('y23d23.test')) == 154

    puzzle = fetch_lines(year=2023, day=23)
    print(f'Part 1: {part1(puzzle)}')
    print(f'Part 2: {part2(puzzle)}')
