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
    from faoci.interface import fetch_lines
    assert paper_required(2, 3, 4) == 58
    assert total_paper_required(['2x3x4']) == 58
    assert total_paper_required(['1x1x10']) == 43

    assert total_ribbon_required(['2x3x4']) == 34
    assert total_ribbon_required(['1x1x10']) == 14

    print(total_paper_required(fetch_lines(year=2015, day=2)))
    print(total_ribbon_required(fetch_lines(year=2015, day=2)))
