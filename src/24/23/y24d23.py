# Path: /home/g/Code/advent-of-python/src/24/23/y24d23.py
# Puzzle Source: https://adventofcode.com/2024/day/23
from dataclasses import dataclass, field
from typing import TypeVar, Any
from functools import cache
from networkx import Graph


def load_lines(named: str):
    from pathlib import Path
    with Path(__file__).parent.joinpath(f'{named}.test').open('r') as f:
        lines = f.read().split('\n')
    return lines[:-1] if len(lines[-1]) == 0 else lines


def build_network(lines: list[str]):
    g = Graph()
    g.add_edges_from([line.split('-') for line in lines])
    return g

def t3_count(graph: Graph):
    from itertools import combinations
    nodes = {n: list(graph.neighbors(n)) for n in graph.nodes}
    t_deg = {n: graph.degree(n) for n in graph.nodes if n.startswith('t')}
    total, double, triple = 0, 0, 0
    for c in t_deg:
        for a, b in combinations(nodes[c], 2):
            if a in nodes[b]:
                if a.startswith('t') and b.startswith('t'):
                    triple += 1
                elif a.startswith('t') or b.startswith('t'):
                    double += 1
                total += 1
    return total - double // 2 - 2 * triple // 3


def find_password(graph: Graph):
    from networkx import max_weight_clique
    nodes, weight = max_weight_clique(graph, weight=None)
    return ','.join(sorted(nodes))
    


def part1(lines: list[str]) -> int:
    return t3_count(build_network(lines))


def part2(lines: list[str]) -> int:
    return find_password(build_network(lines))


if __name__ == '__main__':
    from faoci.interface import fetch_lines

    assert part1(load_lines('y24d23')) == 7

    puzzle = fetch_lines(year=2024, day=23)
    print(f'Part 1: {part1(puzzle)}')
    print(f'Part 2: {part2(puzzle)}')
