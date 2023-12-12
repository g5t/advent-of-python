from enum import Enum, auto
from dataclasses import dataclass, field


class PT(Enum):
    ns = auto()      # |
    ew = auto()      # -
    ne = auto()      # L
    nw = auto()      # J
    sw = auto()      # 7
    se = auto()      # F
    ground = auto()  # .
    start = auto()   # S
    star = auto()    # *
    inside = auto()  # I
    outside = auto   # O

    def perp(self):
        pairs = {PT.ns: PT.ew, PT.ne: PT.sw, PT.nw: PT.se}
        if self in pairs:
            return pairs[self]
        pairs = {v: k for k, v in pairs.items()}
        if self in pairs:
            return pairs[self]
        return self

    @classmethod
    def char2enum(cls):
        return {'|': PT.ns, '-': PT.ew, 'L': PT.ne, 'J': PT.nw, '7': PT.sw, 'F': PT.se, '.': PT.ground, 'S': PT.start,
                '*': PT.star, 'I': PT.inside, 'O': PT.outside}

    @classmethod
    def enum2char(cls):
        return {PT.ns: '║', PT.ew: '═', PT.ne: '╚', PT.nw: '╝', PT.sw: '╗', PT.se: '╔', PT.ground: ' ', PT.start: '╬',
                PT.star: '*', PT.inside: '▓', PT.outside: '▒'}

    def __str__(self):
        return self.enum2char()[self]

    def chars(self) -> list[str]:
        if self == PT.start:
            return ['n', 's', 'e', 'w']
        if self == PT.ground:
            return []
        return [x for x in self.name]

    @classmethod
    def decode(cls, c: str):
        pairs = cls.char2enum()
        if any(x not in pairs for x in c):
            raise ValueError(f'Non-pipe character(s) present in "{c}"')
        return [pairs[x] for x in c if x in pairs]

    @classmethod
    def from_neighbors(cls, me: tuple[int, int], a: tuple[int, int], b: tuple[int, int]):
        pair = []
        for x in (a, b):
            if x[0] == me[0] and x[1] + 1 == me[1]:
                pair.append('n')
            if x[0] == me[0] and x[1] - 1 == me[1]:
                pair.append('s')
            if x[1] == me[1] and x[0] - 1 == me[0]:
                pair.append('w')
            if x[1] == me[1] and x[0] + 1 == me[0]:
                pair.append('e')
        if len(pair) != 2:
            raise ValueError('Points are not neighbors of a valid pipe!')
        if 'n' in pair:
            if 's' in pair:
                return PT.ns
            if 'e' in pair:
                return PT.ne
            if 'w' in pair:
                return PT.nw
        if 's' in pair:
            if 'e' in pair:
                return PT.se
            if 'w' in pair:
                return PT.sw
        if 'w' in pair and 'e' in pair:
            return PT.ew
        raise ValueError(f'Unknown pair {pair}')


@dataclass
class Boundary:
    _edge: list[tuple[int, int]]

    def contains(self, point: tuple[float, float]):
        winding = 0
        for i in range(len(self._edge)):
            if point[0] != self._edge[i][0] and point[0] != self._edge[(i+1) % len(self._edge)][0]:
                continue
            p0 = self._edge[i]
            p1 = self._edge[(i+1) % len(self._edge)]
            # # we already filtered for this:
            # if point == p0 or point == p1:
            #     return False
            # the point-different vector is only ever one of (0,1), (0,-1), (1,0), or (-1,0)
            # but we only care about the vertical component (and don't mind adding the horizontal 0)
            if point[1] < p0[1] or point[1] < p1[1]:
                winding += p1[0] - p0[0]
        return winding != 0


@dataclass
class PipeMap:
    _map: list[list[PT]] = field(default_factory=list)
    _start: tuple[int, int] = (-1, -1)

    def __str__(self):
        return '\n'.join(''.join(str(x) for x in line) for line in self._map)

    @property
    def rows(self):
        return len(self._map)

    @property
    def cols(self):
        return len(self._map[0]) if self.rows else 0

    def indexes(self):
        from itertools import product
        return product(range(self.rows), range(self.cols))

    def __post_init__(self):
        if self._start == (-1, -1):
            starts = [(r, c) for r, c in self.indexes() if self._map[r][c] == PT.start]
            if len(starts) != 1:
                raise ValueError(f'Expected exactly one starting point, found {starts}')
            self._start = starts[0]

    @classmethod
    def from_strings(cls, strings: list[str]):
        lines = [PT.decode(line) for line in strings if len(line)]
        if any(len(line) != len(lines[0]) for line in lines):
            raise ValueError(f'{cls.__name__} is not regular')
        return cls(lines)

    def options(self, pos: tuple[int, int]) -> list[tuple[int, int]]:
        row, col = pos
        x = self._map[row][col]
        dirs = {'n': (-1, 0), 'e': (0, 1), 's': (1, 0), 'w': (0, -1)}
        ops = {'n': 's', 's': 'n', 'e': 'w', 'w': 'e'}
        check_dirs = {c: dirs[c] for c in x.chars()}
        check_idxs = {d: (row+v[0], col+v[1]) for d, v in check_dirs.items()
                      if 0 <= (row + v[0]) < self.rows and 0 <= (col + v[1]) < self.cols}
        opts = [(r, c) for d, (r, c) in check_idxs.items() if ops[d] in self._map[r][c].chars()]
        return opts

    def find_loop(self):
        dist = {self._start: 0}  # key = pos
        tail = {}  # key = pos
        opts = [(self._start, x) for x in self.options(self._start)]
        for opt in opts:
            dist[opt[1]] = 1  # all first options are 1 step from the start, by definition
            tail[opt[1]] = opt[0]

        # breadth-first
        while len(opts):
            at, to = opts.pop(0)
            accepted = [(to, x) for x in self.options(to) if x not in dist]
            for opt in accepted:
                dist[opt[1]] = dist[to] + 1
                tail[opt[1]] = to
            opts.extend(accepted)

        # The end of our search has the highest value
        highest = max(dist.values())
        end = [k for k in dist.keys() if dist[k] == highest][0]
        # we can use the tail map to find our way back along one half
        rpath = [end]
        key = end
        while key in tail:
            key = tail[key]
            rpath.append(key)
        path = list(reversed(rpath))
        # but the other side is trickier
        near_ends = [k for k in dist.keys() if dist[k] == highest - 1 and tail[end] != k]
        if len(near_ends) > 1:
            raise ValueError('what do here?')
        key = near_ends[0]
        while key in tail:
            path.append(key)
            key = tail[key]  # intentionally different from above to avoid double-counting start-point

        return path

    def find_loop_length(self):
        loop = self.find_loop()
        return len(loop)

    def perp(self, pos: tuple[int, int]) -> tuple[int, int]:
        dirs = {PT.ns: (-1, 0), PT.ew: (0, 1), PT.ne: (-1, 1), PT.nw: (-1, 1), PT.se: (1, 1), PT.sw: (1, -1)}
        pt = self._map[pos[0]][pos[1]]
        if pt == PT.start:
            raise ValueError('Replace the start point in the map before using this method!')
        return dirs.get(pt.perp(), (0, 0))


    def eroded_loop(self):
        # each point needs to take a half-step in its perpendicular direction *towards the inside of the loop*
        # to calculate the 'full' square area correctly.
        # inside can be determined using winding number, but a simpler check might suffice:
        sign = {}
        dirs = {}
        loop = self.find_loop()

        # replace the starting point in the map with the piece that it must be:
        self._map[loop[0][0]][loop[0][1]] = PT.from_neighbors(loop[0], loop[1], loop[-1])

        bound = Boundary(loop)
        # skip the start point for now
        skipped = [0, 1]
        for i in range(2, len(loop) + 2):
            prev, this, follow = [loop[(i + x) % len(loop)] for x in (-1, 0, 1)]
            before, here, after = [self.perp(x) for x in (prev, this, follow)]
            if before == here and prev in sign:
                sign[this] = sign[prev]
            elif after == here and follow in sign:
                sign[this] = sign[follow]
            elif prev in sign or follow in sign:
                s, d = (sign[prev], before) if prev in sign else (sign[follow], after)
                db = here[0] * s * d[0] + here[1] * s * d[1]
                if db == 0:
                    raise ValueError('Neighbors can not have zero perpendicular do product!')
                sign[this] = 1 if db > 0 else -1
            else:
                # we must use the winding number.
                sign[this] = 1 if bound.contains((this[0] + 0.5 * here[0], this[1] + 0.5 * here[1])) else -1

        if any(x not in sign for x in loop):
            raise ValueError("Unhandled loop points")

        eroded = [(p[0] + 0.5 * sign[p] * self.perp(p)[0], p[1] + 0.5 * sign[p] * self.perp(p)[1]) for p in loop]
        return eroded

    def find_loop_area(self):
        # We can use Green's theorem for a vector field with constant partial-derivative differences
        # dFy/dx - dFx/dy = 1, e.g., F = (Fx, Fy) = Fx xhat + Fy yhat == (-y/2, x/2)
        # Then the area is the integral of F . ds around the boundary, e.g., the loop we found
        loop = self.find_loop()
        Fds = [loop[i][0] * (loop[i][1] - loop[i-1][1]) - loop[i][1] * (loop[i][0] - loop[i-1][0])
               for i in range(1, len(loop))]
        area = sum(Fds) / 2
        return area

    def count_contained_points(self):
        loop = self.find_loop()
        boundary = Boundary(loop)
        print()
        print(self)
        for point in self.indexes():
            if point not in loop:
                self._map[point[0]][point[1]] = PT.ground
                if boundary.contains(point):
                    self._map[point[0]][point[1]] = PT.star
        print()
        print(self)
        return sum(1 for point in self.indexes() if self._map[point[0]][point[1]] == PT.star)


def read_input(filename):
    with open(filename, 'r') as file:
        lines = file.read().splitlines()
    return PipeMap.from_strings(lines)


def part1(pipe_map: PipeMap):
    return pipe_map.find_loop_length() // 2


def part2(pipe_map: PipeMap):
    return pipe_map.count_contained_points()


def main():
    pipes = read_input('y23d10.txt')
    print(part1(pipes))
    print(part2(pipes))


if __name__ == '__main__':
    assert part1(read_input('y23d10a.test')) == 4
    assert part1(read_input('y23d10b.test')) == 8
    assert part1(read_input('y23d10c.test')) == 8
    assert part2(read_input('y23d10a.test')) == 1
    assert part2(read_input('y23d10d.test')) == 4
    assert part2(read_input('y23d10e.test')) == 8
    assert part2(read_input('y23d10f.test')) == 10

    main()
