def read_input(filename: str) -> list[list[int]]:
    with open(filename, 'r') as f:
        lines = f.readlines()
    lines = [[int(x) for x in line.strip().split()] for line in lines if len(line.strip())]
    return lines


def listdiff(values: list):
    return [b - a for a, b in zip(values, values[1:])]


def sequence_guess(first: list):
    v = listdiff(first)
    values = [first]
    while any(x != 0 for x in v):
        if len(v) < 2:
            raise RuntimeError("Sequence did not finish!")
        values.append(list(v))
        v = listdiff(v)

    rvalues = list(reversed(values))
    for a, b in zip(rvalues, rvalues[1:]):
        b.append(b[-1] + a[-1])

    return values[0][-1]


def part1(lines: list[list[int]]) -> int:
    return sum(sequence_guess(x) for x in lines)


def part2(lines: list[list[int]]) -> int:
    return sum(sequence_guess(list(reversed(x))) for x in lines)


def main():
    lines = read_input('y23d09.txt')
    print(part1(lines))
    print(part2(lines))


if __name__ == '__main__':
    test_data = read_input('y23d09.test')
    assert part1(test_data) == 114
    assert part2(test_data) == 2
    main()


