# Path: /home/g/Code/advent-of-python/src/24/02/y24d02.py
# Puzzle Source: https://adventofcode.com/2024/day/2


def get_levels(line: str) -> list[int]:
    return [int(x) for x in line.split()]


def safe_levels(levels: list[int]) -> bool:
    inc = levels[1] > levels[0]
    for i in range(1, len(levels)):
        a, b = levels[i-1], levels[i]
        if a == b or (b > a) != inc or abs(a-b) > 3:
            return False
    return True


def ok_if_remove_any_one(x: list[int]) -> bool:
    for i in range(len(x)):
        if safe_levels([*x[:i], *x[i+1:]]):
            return True
    return False


def dampen_levels(levels: list[int]) -> bool:
    inc = levels[1] > levels[0]
    for i in range(1, len(levels)):
        a, b = levels[i-1], levels[i]
        if a == b or (b > a) != inc or abs(a-b) > 3:
            return ok_if_remove_any_one(levels)
    return True


def part1(lines: list[str]) -> int:
    return sum(safe_levels(get_levels(line)) for line in lines)


def part2(lines: list[str]) -> int:
    return sum(dampen_levels(get_levels(line)) for line in lines)


if __name__ == '__main__':
    from faoci.interface import fetch_lines

    print(f'Part 1: {part1(fetch_lines(year=2024, day=2))}')
    print(f'Part 2: {part2(fetch_lines(year=2024, day=2))}')
