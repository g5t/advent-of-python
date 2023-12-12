from functools import lru_cache


@lru_cache
def fits(size: int, line: str) -> bool:
    if size > len(line):
        return False
    # A known-good spring can not be in the group:
    if line.find('.', 0, size) >= 0:
        return False
    # A cluster either fills to the end or is followed by an unknown or good spring
    return '#' != line[size] if len(line) > size else True


@lru_cache
def check(line: str, counts: tuple[int, ...]) -> int:
    if sum(counts) + len(counts) - 1 > len(line):
        # no chance to fit in all the broken springs:
        return 0
    if len(counts) == 1:
        # bottom layer, special handling
        last = 1 if fits(counts[0], line) and line.find('#', counts[0]) < 0 else 0
        keep = 0 if '#' == line[0] else check(line[1:], counts)
        return last + keep
    # if we can fit a group at the current position, do:
    yes = check(line[(counts[0] + 1):], counts[1:]) if fits(counts[0], line) else 0
    # if we _need_ to fit a group at the current position but can't, stop; otherwise try the next spot
    no = 0 if '#' == line[0] else check(line[1:], counts)
    return yes + no


def enter(line: str, repeat: int = 1) -> int:
    code, meta = line.strip().split(' ')
    short = code
    # short = '.'.join(filter(lambda x: len(x), code.split('.')))
    counts = tuple(int(x) for x in meta.split(','))
    full_line = '?'.join(short for _ in range(repeat))
    full_counts = counts * repeat
    return check(full_line, full_counts)


def read_values(filename) -> list[str]:
    from pathlib import Path
    if not Path(filename).exists():
        return []
    with open(filename, 'r') as f:
        lines = f.readlines()
    return [line.strip() for line in lines if len(line.strip())]


def part(values: list[str], number: int = 1):
    return sum(enter(line, repeat=5 if number == 2 else 1) for line in values)


if __name__ == '__main__':
    assert enter('???.### 1,1,3') == 1
    assert enter('.??..??...?##. 1,1,3') == 4
    assert enter('?###???????? 3,2,1') == 10
    assert enter('?.#.??##???### 1,3,4') == 2
    assert enter('?????.?.?????##?#.?? 3,5') == 4
    assert enter('?#?.???.??? 3') == 1
    assert enter('??????#?.??? 4,3') == 3
    assert enter('??????#?.???.??? 4,3') == 5
    assert enter('??.#####?..???#.##?. 1,6,2,1,3') == 2
    assert enter('?????##?##????.???? 1,9,2,1,1') == 3

    test_values = read_values('y23d12.test')
    assert part(test_values) == 21
    assert part(test_values, number=2) == 525152

    puzzle = read_values('y23d12.txt')
    print(part(puzzle))
    print(part(puzzle, number=2))
