# Path: /home/gst/PycharmProjects/aoc23/src/23/15/y23d15.py
# Puzzle Source: https://adventofcode.com/2023/day/15
from dataclasses import dataclass, field


@dataclass
class LensBox:
    _lenses: dict[str, int] = field(default_factory=dict)  # dictionaries are ordered from Python 3.6

    def __setitem__(self, key, value):
        self._lenses[key] = value

    def remove(self, lens: str):
        if lens in self._lenses:
            del self._lenses[lens]

    def power(self):
        return sum((i+1) * x for i, x in enumerate(self._lenses.values()))


def box_hash(string: str) -> int:
    result = 0
    for c in string:
        result = (17 * (result + ord(c))) % 256
    return result


def part1(strings: str) -> int:
    return sum(box_hash(x) for x in strings.split(','))


def part2(instructions: str) -> int:
    boxes = tuple(LensBox() for _ in range(256))
    for instruction in instructions.split(','):
        if '=' in instruction:
            name, focal_length = instruction.split('=', 1)
            boxes[box_hash(name)][name] = int(focal_length)
        if '-' in instruction:
            name = instruction[:-1]
            boxes[box_hash(name)].remove(name)
    total_power = sum((i+1) * box.power() for i, box in enumerate(boxes))
    return total_power


if __name__ == '__main__':
    from faoci.interface import fetch_lines

    assert box_hash('rn=1') == 30
    assert box_hash('cm-') == 253
    assert box_hash('qp=3') == 97
    assert part1('rn=1,cm-,qp=3,cm=2,qp-,pc=4,ot=9,ab=5,pc-,pc=6,ot=7') == 1320
    assert part2('rn=1,cm-,qp=3,cm=2,qp-,pc=4,ot=9,ab=5,pc-,pc=6,ot=7') == 145

    print(f'Part 1: {part1(fetch_lines(year=2023, day=15)[0])}')
    print(f'Part 2: {part2(fetch_lines(year=2023, day=15)[0])}')
