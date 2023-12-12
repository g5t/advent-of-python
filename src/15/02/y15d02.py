def paper_required(d, w, h):
    return 2 * d * w + 2 * d * h + 2 * w * h + d * w


def ribbon_required(d, w, h):
    return 2 * d + 2 * w + d * w * h


def read_lengths(line: str):
    lengths = tuple(sorted([int(x) for x in line.strip().split('x')]))
    return lengths


def total_paper_required(lines: list[str]):
    return sum(paper_required(*read_lengths(line)) for line in lines)

def total_ribbon_required(lines: list[str]):
    return sum(ribbon_required(*read_lengths(line)) for line in lines)


if __name__ == '__main__':
    assert paper_required(2, 3, 4) == 58
    assert total_paper_required(['2x3x4']) == 58
    assert total_paper_required(['1x1x10']) == 43

    assert total_ribbon_required(['2x3x4']) == 34
    assert total_ribbon_required(['1x1x10']) == 14

    with open('y15d02.txt', 'r') as file:
        puzzle = file.readlines()

    print(total_paper_required(puzzle))
    print(total_ribbon_required(puzzle))
