# Path: /home/gst/PycharmProjects/aoc23/src/23/19/y23d19.py
# Puzzle Source: https://adventofcode.com/2023/day/19
from __future__ import annotations
from dataclasses import dataclass, field


@dataclass
class Rule:
    _property: str
    _comparison: str
    _value: int
    _destination: str

    @property
    def destination(self):
        return self._destination

    @classmethod
    def from_string(cls, s: str):
        n, d = s[2:].split(':')
        return Rule(s[0], s[1], int(n), d)

    def __call__(self, part):
        if self._comparison == '>':
            if part[self._property] > self._value:
                return self._destination
        elif self._comparison == '<':
            if part[self._property] < self._value:
                return self._destination
        else:
            raise ValueError(f'Unknown comparer {self._comparison}')
        return None

    def limits(self, rating: Space) -> tuple[Space | None, Space | None]:
        passed, failed = rating.split(self._property, self._value, self._comparison)
        return passed, failed


@dataclass
class Method:
    _name: str
    _rules: tuple[Rule, ...]
    _final: str

    def __post_init__(self):
        # If all methods have the same end point, we can simplify this rule set
        if all(x.destination == self._final for x in self._rules):
            self._rules = tuple()

    @property
    def name(self):
        return self._name

    @classmethod
    def from_string(cls, s: str):
        name, rest = s.split('{', 1)
        rules = rest.strip('}').split(',')
        method = tuple([Rule.from_string(x) for x in rules[:-1]])
        return Method(name, method, rules[-1])

    def __call__(self, part):
        if isinstance(part, Part):
            for rule in self._rules:
                if (res := rule(part)) is not None:
                    return res
            return self._final

    def limits(self, ratings: list[Space]) -> dict[str, list[Space]]:
        results = {self._final: []}
        for rating in ratings:
            failed = rating
            for rule in self._rules:
                passed, failed = rule.limits(failed)
                if passed:
                    dest = results.get(rule.destination, [])
                    dest.append(passed)
                    results[rule.destination] = dest
                if failed is None:
                    break
            if failed is not None and self._final != 'R':
                results[self._final].append(failed)
        return results


@dataclass
class Procedure:
    _steps: dict[str, Method]
    _start: str

    @classmethod
    def from_lines(cls, lines: list[str], start: str | None = None):
        methods = [Method.from_string(line) for line in lines]
        return Procedure({x.name: x for x in methods}, start or 'in')

    def __call__(self, part):
        dest = self._steps[self._start](part)
        while dest in self._steps:
            dest = self._steps[dest](part)
        if dest == 'R':
            return 0
        if dest == 'A':
            return 1
        raise ValueError(f'Unexpected end to rules at {dest}')

    def limits(self, property_ranges: Space) -> list[Space]:
        accepted = []
        remaining = self._steps[self._start].limits([property_ranges])
        while len(remaining):
            handled = {}
            for dest, r in remaining.items():
                if dest == 'A':
                    accepted.extend(r)
                elif dest == 'R':
                    pass
                elif dest in self._steps:
                    temp = self._steps[dest].limits(r)
                    for k, v in temp.items():
                        store = handled.get(k, [])
                        store.extend(v)
                        handled[k] = store
                else:
                    raise ValueError(f'Unexpected rule destination {dest}')
            remaining = handled
        return accepted


@dataclass
class Part:
    _x: int
    _m: int
    _a: int
    _s: int

    @classmethod
    def from_string(cls, s: str):
        return Part.from_dict({k: int(v) for k, v in [pair.split('=') for pair in s.strip('{}').split(',')]})

    @classmethod
    def from_dict(cls, d: dict[str, int]):
        return Part(d['x'], d['m'], d['a'], d['s'])

    def __getitem__(self, item):
        return getattr(self, f'_{item}')

    @property
    def rating(self):
        return self._x + self._m + self._a + self._s


@dataclass
class Range:
    _min: int = 1
    _max: int = 4000

    def __post_init__(self):
        if self._max < self._min:
            raise ValueError('Reversed RatingRange?')

    def split(self, value: int, op: str) -> tuple[Range | None, Range | None]:
        if '<' == op:
            # (min, max) < value
            if self._max < value:
                return self, None
            if self._min >= value:
                return None, self
            return Range(self._min, value - 1), Range(value, self._max)
        elif '>' == op:
            # (min, max) > value
            if self._min > value:
                return self, None
            if self._max <= value:
                return None, self
            return Range(value + 1, self._max), Range(self._min, value)
        raise ValueError(f'Unexpected operation {op}')

    @property
    def count(self):
        return self._max - self._min + 1


@dataclass
class Space:
    _x: Range = field(default_factory=Range)
    _m: Range = field(default_factory=Range)
    _a: Range = field(default_factory=Range)
    _s: Range = field(default_factory=Range)

    def __getitem__(self, item):
        return getattr(self, f'_{item}')

    def __setitem__(self, key, value):
        setattr(self, f'_{key}', value)

    def copy(self):
        return Space(self._x, self._m, self._a, self._s)

    def split(self, p: str, value: int, op: str) -> tuple[Space | None, Space | None]:
        a, b = self.copy(), self.copy()
        a[p], b[p] = self[p].split(value, op)
        return a if a[p] else None, b if b[p] else None

    @property
    def count(self):
        prod = 1
        for x in ('x', 'm', 'a', 's'):
            prod *= self[x].count
        return prod


def read_procedure_parts(lines: list[str]) -> tuple[Procedure, list[Part]]:
    rule_lines, part_lines = [], []
    is_rule = True
    for line in lines:
        if len(line.strip()) == 0:
            is_rule = False
        elif is_rule:
            rule_lines.append(line)
        else:
            part_lines.append(line)
    return Procedure.from_lines(rule_lines), [Part.from_string(line) for line in part_lines]


def get_lines(filename):
    from pathlib import Path
    if isinstance(filename, str):
        filename = Path(filename)
    filename = filename.resolve()
    if not filename.exists():
        return []

    with open(filename, 'r') as file:
        return file.read().splitlines()


def part1(lines: list[str]) -> int:
    rules, parts = read_procedure_parts(lines)
    return sum(rules(x) * x.rating for x in parts)


def part2(lines: list[str]) -> int:
    rules, _ = read_procedure_parts(lines)
    ranges = rules.limits(Space())
    return sum(r.count for r in ranges)


if __name__ == '__main__':
    from faoci.interface import fetch_lines

    assert part1(get_lines('y23d19.test')) == 19114

    assert part2(get_lines('y23d19a.test')) == 2000 * 2000 * 2000 * 2000
    assert part2(get_lines('y23d19.test')) == 167409079868000

    puzzle = fetch_lines(year=2023, day=19)
    print(f'Part 1: {part1(puzzle)}')
    print(f'Part 2: {part2(puzzle)}')
