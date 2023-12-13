# Path: 2015/03/y2015d03.py
# Puzzle Source: https://adventofcode.com/2015/day/3
def get_lines(filename):
    from pathlib import Path
    if isinstance(filename, str):
        filename = Path(filename)
    filename = filename.resolve()
    if not filename.exists():
        return []

    with open(filename, 'r') as file:
        return file.read().splitlines()


def instruction(c: str) -> tuple[int, int]:
    instructions = {'>': (0, 1), '<': (0, -1), 'v': (1, 0), '^': (-1, 0)}
    return instructions[c]


def part1(lines: list[str]) -> int:
    last = (0, 0)
    visited = {last}
    for x in lines[0]:
        d = instruction(x)
        last = last[0] + d[0], last[1] + d[1]
        visited.add(last)
    return len(visited)


def part2(lines: list[str]) -> int:
    santa, robo = (0, 0), (0, 0)
    visited = {santa, robo}
    for i, x in enumerate(lines[0]):
        d = instruction(x)
        if (i % 2) == 1:
            robo = robo[0] + d[0], robo[1] + d[1]
            visited.add(robo)
        else:
            santa = santa[0] + d[0], santa[1] + d[1]
            visited.add(santa)
    return len(visited)


if __name__ == '__main__':
    from faoci.interface import fetch_lines

    assert part1(['>']) == 2
    assert part1(['^>v<']) == 4
    assert part1(['^v^v^v^v^v']) == 2

    assert part2(['^v']) == 3
    assert part2(['^>v<']) == 3
    assert part2(['^v^v^v^v^v']) == 11

    puzzle = fetch_lines(year=2015, day=3)
    for line in puzzle:
        print(line)
    print(f'Part 1: {part1(puzzle)}')
    print(f'Part 2: {part2(puzzle)}')

