# Path: /home/g/Code/advent-of-python/src/24/03/y24d03.py
# Puzzle Source: https://adventofcode.com/2024/day/3


def example():
    return "xmul(2,4)%&mul[3,7]!@^do_not_mul(5,5)+mul(32,64]then(mul(11,8)mul(8,5))"


def example2():
    return "xmul(2,4)&mul[3,7]!^don't()_mul(5,5)+mul(32,64](mul(11,8)undo()?mul(8,5))"


def extract_muls_instr(lines: list[str], instr: bool=False) -> int:
    import re
    r = re.compile(r"(?P<off>don't\(\))|(?P<on>do\(\))|(?P<mul>mul\((?P<left>[0-9]+),(?P<right>[0-9]+)\))")
    total = 0
    on = True
    for line in lines:
        for m in r.finditer(line):
            gd = m.groupdict()
            if instr and (gd['on'] is not None):
                on = True
            elif instr and (gd['off'] is not None):
                on = False
            elif on and (gd['left'] is not None) and (gd['right'] is not None):
                total += int(gd['left']) * int(gd['right'])
    return total


def part1(lines: list[str]) -> int:
    return extract_muls_instr(lines)

def part2(lines: list[str]) -> int:
    return extract_muls_instr(lines, instr=True)


if __name__ == '__main__':
    from faoci.interface import fetch_lines

    assert part1([example()]) == 161
    assert part2([example2()]) == 48

    print(f'Part 1: {part1(fetch_lines(year=2024, day=3))}')
    print(f'Part 2: {part2(fetch_lines(year=2024, day=3))}')
