# Path: /home/g/Code/advent-of-python/src/24/04/y24d04.py
# Puzzle Source: https://adventofcode.com/2024/day/4

class D:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __add__(self, other):
        return D(self.x + other.x, self.y + other.y)
    
    def __sub__(self, other):
        return D(self.x - other.x, self.y - other.y)

    def __mul__(self, integer):
        return D(self.x * integer, self.y * integer)

    def inbound(self, board: list[str]):
        return self.x >= 0 and self.x < len(board) and self.y >= 0 and self.y < len(board[self.x])

    def is_chr(self, board: list[str], c: chr):
        return self.inbound(board) and c == board[self.x][self.y]

    def status(self, board: list[str]):
        return board[self.x][self.y] if self.inbound(board) else '_'


def directions():
    n, e, s, w = D(-1, 0), D(0, 1), D(1, 0), D(0, -1)
    return n, n+e, e, s+e, s, s+w, w, n+w


def is_all(board: list[str], xs: tuple[D], cs: tuple[chr]) -> bool:
    return all(x.is_chr(board, c) for x, c in zip(xs, cs))


def is_xmas(board: list[str], x0: D, d: D):
    return is_all(board, (x0, x0 + d, x0 + d * 2, x0 + d * 3),  ('X', 'M', 'A', 'S'))


def is_x_mas(board: list[str], x0: D, d1: D, d2: D):
    return is_all(board, (x0 - d1, x0 - d2, x0, x0 + d2, x0 + d1), ('M', 'M', 'A', 'S', 'S'))


def xmas_count(board: list[str], v: D):
    return sum(is_xmas(board, v, d) for d in directions())


def x_mas_count(board: list[str], v: D):
    _, ne, _, se, _, sw, _, nw = directions()
    return sum(is_x_mas(board, v, a, b) for a, b in ((ne, se), (ne, nw), (nw, sw), (se, sw)))


def positions(board: list[str]) -> list[D]:
    return [D(x, y) for x, line in enumerate(board) for y in range(len(line))]


def part1(board: list[str]) -> int:
    return sum(xmas_count(board, v) for v in positions(board))


def part2(board: list[str]) -> int:
    return sum(x_mas_count(board, v) for v in positions(board))


if __name__ == '__main__':
    from faoci.interface import fetch_lines

    print(f'Part 1: {part1(fetch_lines(year=2024, day=4))}')
    print(f'Part 2: {part2(fetch_lines(year=2024, day=4))}')
