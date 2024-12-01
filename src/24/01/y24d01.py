# Path: /home/g/Code/advent-of-python/src/24/01/y24d01.py
# Puzzle Source: https://adventofcode.com/2024/day/1

def id_lists(lines: list[str]):
    left_right = [[int(n) for n in x.split(maxsplit=1)] for x in lines]
    left, right = [[x[i] for x in left_right] for i in (0, 1)]
    return left, right


def part1(lines: list[str]) -> int:
    left, right = [sorted(x) for x in id_lists(lines)]
    return sum([abs(x - y) for x, y in zip(left, right)])


def part2(lines: list[str]) -> int:
    left, right = id_lists(lines)
    multiplier = {}
    for r in right:
        multiplier[r] = multiplier.get(r, 0) + 1
    return sum([x * multiplier.get(x, 0) for x in left])


if __name__ == '__main__':
    from faoci.interface import fetch_lines

    print(f'Part 1: {part1(fetch_lines(year=2024, day=1))}')
    print(f'Part 2: {part2(fetch_lines(year=2024, day=1))}')
