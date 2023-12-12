def find_floor(instructions: str):
    up = instructions.count('(')
    down = instructions.count(')')
    return up - down


def enters_basement_at(instructions: str):
    for i in range(len(instructions)+1):
        if find_floor(instructions[:i]) == -1:
            return i
    return 0


def part1(values):
    print(values)
    value = find_floor(values)
    print(value)


def part2(values):
    print(enters_basement_at(values))


if __name__ == '__main__':
    assert find_floor('(())') == 0
    assert find_floor('()()') == 0
    assert find_floor('(((') == 3
    assert find_floor('(()(()(') == 3
    assert find_floor('))(((((') == 3
    assert find_floor('())') == -1

    assert enters_basement_at(')') == 1
    assert enters_basement_at('()())') == 5

    with open('input.txt') as file:
        data = file.readlines()[0]

    part1(data)
    part2(data)