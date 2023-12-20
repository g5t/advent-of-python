# Path: /home/gst/PycharmProjects/aoc23/src/23/20/y23d20.py
# Puzzle Source: https://adventofcode.com/2023/day/20
from __future__ import annotations
from dataclasses import dataclass, field
from enum import Enum, auto
from typing import TypeVar


class Pulse(Enum):
    low = auto()
    high = auto()


ModuleType = TypeVar('ModuleType', bound='Module')


@dataclass
class Message:
    call: int
    dest: int
    pulse: Pulse

@dataclass
class Module:
    name: str
    _ptr: int
    _dest: tuple[int, ...]

    def __call__(self, caller: int, pulse: Pulse, push_count: int) -> list[Message]:
        return self.compose(pulse)

    def walk(self, caller: int) -> list[tuple[int, int]]:
        return [(self._ptr, d) for d in self._dest]

    def compose(self, pulse: Pulse) -> list[Message]:
        return [Message(self._ptr, ptr, pulse) for ptr in self._dest]


@dataclass
class FlipFlop(Module):
    state: bool = False

    def __call__(self, caller: int, pulse: Pulse, push_count: int) -> list[Message]:
        if Pulse.low == pulse:
            send = Pulse.low if self.state else Pulse.high
            self.state = not self.state
            return self.compose(send)
        return []


@dataclass
class Conjunction(Module):
    state: dict[int, Pulse] = field(default_factory=dict)
    first: dict[int, int | None] = field(default_factory=dict)

    def __call__(self, caller: int, pulse: Pulse, push_count: int):
        self.state[caller] = pulse
        if Pulse.high == pulse:
            if self.first[caller] is None:
                self.first[caller] = push_count
        send = Pulse.low if all(Pulse.high == x for x in self.state.values()) else Pulse.high
        return self.compose(send)

    def walk(self, caller: int) -> list[tuple[int, int]]:
        self.state[caller] = Pulse.low
        self.first[caller] = None
        return super().walk(caller)

    def pushes_to_flip(self) -> int | None:
        # There is no requirement that each input to a node sends a high-signal with a fixed frequency
        # However, this is miraculously good enough for _my_ input to solve part 2:
        if any(x is None for x in self.first.values()):
            return None
        prod = 1
        for x in self.first.values():
            prod *= x
        return prod


@dataclass
class Broadcast(Module):
    pass


@dataclass
class Output(Module):
    caller: int = -1

    def walk(self, caller: int) -> list[tuple[int, int]]:
        if self.caller != -1:
            raise RuntimeError('Output has more than one caller!')
        self.caller = caller
        return []


@dataclass
class Network:
    _nodes: tuple[Module, ...]
    _broadcaster: int = 0

    def __post_init__(self):
        b = [i for i, n in enumerate(self._nodes) if isinstance(n, Broadcast)]
        if len(b) != 1:
            raise ValueError("Exactly one broadcast module required")
        self._broadcaster = b[0]
        self.walk()

    def walk(self):
        to_make = self._nodes[self._broadcaster].walk(-1)
        calls = set(to_make)
        while len(to_make):
            first = to_make.pop(0)  # (caller, destination)
            added = self._nodes[first[1]].walk(first[0])
            added = list(filter(lambda x: x not in calls, added))
            calls.update(added)
            to_make.extend(added)

    def push(self, push_count: int):
        to_make = self._nodes[self._broadcaster](-1, Pulse.low, push_count)
        counts = {Pulse.low: 1, Pulse.high: 0}
        while len(to_make):
            first = to_make.pop(0)  # Message(call, dest, pulse)
            counts[first.pulse] += 1
            added = self._nodes[first.dest](first.call, first.pulse, push_count)
            to_make.extend(added)
        return counts[Pulse.low], counts[Pulse.high]

    def pusher(self, times: int):
        total_low, total_high = 0, 0
        for i in range(times):
            low, high = self.push(i+1)
            total_low += low
            total_high += high

        return total_low, total_high

    def pushes_until_output_receives_low(self):
        output = [i for i, n in enumerate(self._nodes) if isinstance(n, Output)]
        if len(output) != 1:
            return -1
        check = self._nodes[output[0]].caller
        i = 0
        while self._nodes[check].pushes_to_flip() is None:
            i += 1
            self.push(i)
        return self._nodes[check].pushes_to_flip()

    @classmethod
    def from_lines(cls, lines: list[str]):
        named = [line.split(' -> ')[0].strip('&%') for line in lines]
        # output node(s) are also possible!
        destinations = {x.strip() for line in lines for x in line.split(' -> ', 1)[1].split(',')}
        outputs = destinations.difference(named)
        named.extend(outputs)
        nodes = []
        for line in lines:
            a, b = line.split(' -> ')
            if '%' == a[0]:
                t = FlipFlop
            elif '&' == a[0]:
                t = Conjunction
            else:
                t = Broadcast
            ptr = named.index(a.strip('&%'))
            nodes.append(t(named[ptr], ptr, tuple([named.index(x.strip()) for x in b.split(',')])))
        for output in outputs:
            nodes.append(Output(output, named.index(output), ()))
        return Network(tuple(nodes))


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
    net = Network.from_lines(lines)
    low, high = net.pusher(1000)
    return low * high


def part2(lines: list[str]) -> int:
    net = Network.from_lines(lines)
    return net.pushes_until_output_receives_low()


if __name__ == '__main__':
    from faoci.interface import fetch_lines

    assert part1(get_lines('y23d20.test')) == 32000000
    assert Network.from_lines(get_lines('y23d20b.test')).push(1) == (4, 4)
    assert part1(get_lines('y23d20b.test')) == 11687500

    puzzle = fetch_lines(year=2023, day=20)
    print(f'Part 1: {part1(puzzle)}')
    print(f'Part 2: {part2(puzzle)}')
