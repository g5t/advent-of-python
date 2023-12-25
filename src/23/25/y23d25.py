# Path: /home/gst/PycharmProjects/aoc23/src/23/25/y23d25.py
# Puzzle Source: https://adventofcode.com/2023/day/25
from dataclasses import dataclass, field


@dataclass
class DoubleGraph:
    nodes: tuple[str, ...]
    edges: tuple[tuple[int, int], ...]

    @classmethod
    def from_lines(cls, lines: list[str]):
        tr = str.maketrans('', '', ',:')
        nodes = tuple(set(x for line in lines for x in line.translate(tr).split()))
        pairs = set()
        for line in lines:
            first, rest = line.split(':', 1)
            i = nodes.index(first)
            for second in rest.split():
                j = nodes.index(second.strip())
                pairs.add((min(i, j), max(i, j)))
        return cls(nodes, tuple(pairs))

    # def cut_three(self, three: tuple[str, str, str]):
    #     i, j, k = [self.nodes.index(x) for x in three]
    #
    #     def es(m):
    #         return [e for e in self.edges if e[0] == m or e[1] == m]
    #
    #     i_e, j_e, k_e = [es(x) for x in (i, j, k)]
    #

    def partition(self):
        import networkx as nx
        g = nx.Graph()
        g.add_nodes_from(self.nodes)
        g.add_edges_from([(self.nodes[i], self.nodes[j]) for i, j in self.edges])

        nx.draw(g, with_labels=True)
        import matplotlib.pyplot as plt
        plt.show()

        to_remove = nx.minimum_edge_cut(g)
        if len(to_remove) != 3:
            raise RuntimeError('Expected to cut 3!')
        g.remove_edges_from(to_remove)
        # clust = nx.clustering(g)
        # print(sorted(clust.items(), key=lambda x: x[1]))
        # print(nx.cut_size(g, parts[1]))
        nx.draw(g, with_labels=True)
        plt.show()

        sg = [g.subgraph(s) for s in nx.connected_components(g)]
        if len(sg) != 2:
            raise RuntimeError('Expected 2 disconnected subgraphs')
        prod = 1
        for s in sg:
            prod *= len(s)
        return prod


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
    dg = DoubleGraph.from_lines(lines)
    return dg.partition()


def part2(lines: list[str]) -> int:
    return len(lines)


if __name__ == '__main__':
    from faoci.interface import fetch_lines

    assert part1(get_lines('y23d25.test')) == 54

    puzzle = fetch_lines(year=2023, day=25)
    print(f'Part 1: {part1(puzzle)}')
    print(f'Part 2: {part2(puzzle)}')
