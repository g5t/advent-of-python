# Path: 2015/05/y2015d05.py
# Puzzle Source: https://adventofcode.com/2015/day/5
def str_is_nice(line: str) -> bool:
    for bad in ('ab', 'cd', 'pq', 'xy'):
        if bad in line:
            return False
    if sum(x in 'aeiou' for x in line) < 3:
        return False
    for i in range(len(line)-1):
        if line[i] == line[i+1]:
            return True
    return False


def updated_rule_one_passes(line: str) -> bool:
    for i in range(len(line) - 2):
        for j in range(i+2, len(line)):
            if line[i:i+2] == line[j:j+2]:
                return True
    return False


def updated_rule_two_passes(line: str) -> bool:
    for i in range(len(line) - 2):
        if line[i] == line[i+2]:
            return True
    return False


def updated_str_is_nice(line: str) -> bool:
    if not updated_rule_one_passes(line):
        return False
    if not updated_rule_two_passes(line):
        return False
    return True


def part1(lines: list[str]) -> int:
    return sum(str_is_nice(line) for line in lines)


def part2(lines: list[str]) -> int:
    return sum(updated_str_is_nice(line) for line in lines)


if __name__ == '__main__':
    from faoci.interface import fetch_lines

    assert str_is_nice('ugknbfddgicrmopn')
    assert str_is_nice('aaa')
    assert not str_is_nice('')
    assert not str_is_nice('jchzalrnumimnmhp')
    assert not str_is_nice('haegwjzuvuyypxyu')
    assert not str_is_nice('dvszwmarrgswjxmb')

    assert updated_rule_one_passes('xyxy')
    assert updated_rule_one_passes('aabcdefgaa')
    assert not updated_rule_one_passes('aaa')
    assert updated_str_is_nice('qjhvhtzxzqqjkmpb')
    assert updated_str_is_nice('xxyxx')
    assert not updated_str_is_nice('uurcxstgmygtbstg')
    assert not updated_str_is_nice('ieodomkazucvgmuy')

    puzzle = fetch_lines(year=2015, day=5)
    print(f'Part 1: {part1(puzzle)}')
    print(f'Part 2: {part2(puzzle)}')

