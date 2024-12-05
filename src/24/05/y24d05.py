# Path: /home/g/Code/advent-of-python/src/24/05/y24d05.py
# Puzzle Source: https://adventofcode.com/2024/day/5

def example():
    from pathlib import Path
    with Path(__file__).parent.joinpath('example.txt').open('r') as f:
        lines = f.read().split('\n')
    return lines[:-1] if len(lines[-1]) == 0 else lines

class P:
    def __init__(self):
        self.after = {}
        self.before = {}

    def add_rule(self, rule: tuple[int, int]):
        early, late = rule

        left = self.after.get(early, set())
        left.add(late)
        self.after[early] = left

        right = self.before.get(late, set())
        right.add(early)
        self.before[late] = right

    def check(self, job: list[int]) -> bool:
        for i in range(len(job)):
            one = job[i]
            if one not in self.before:
                continue
            for two in job[i+1:]:
                if two not in self.after:
                    continue
                if two in self.before[one] or one in self.after[two]:
                    return False
        return True

    def fix(self, job: list[int]) -> list[int]:
        followers = {len(self.after[x].intersection(job[:i]+job[i+1:])) if x in self.after else 0: x for i, x in enumerate(job)}
        fixed = [followers[x] for x in sorted(followers, reverse=True)]
        return fixed


def get_rules_jobs(lines: list[str]):
    split_at = next(iter(i for i, line in enumerate(lines) if len(line)==0))
    rlines, jlines = lines[:split_at], lines[split_at+1:]
    rules = P()
    for line in rlines:
        a, b = [int(x) for x in line.split('|')]
        rules.add_rule((a, b))
    jobs = [[int(x) for x in line.split(',')] for line in jlines]
    return rules, jobs


def part1(lines: list[str]) -> int:
    rules, jobs = get_rules_jobs(lines)
    return sum(job[len(job)//2] for job in jobs if rules.check(job))


def part2(lines: list[str]) -> int:
    rules, jobs = get_rules_jobs(lines)
    return sum(rules.fix(job)[len(job)//2] for job in jobs if not rules.check(job))


if __name__ == '__main__':
    from faoci.interface import fetch_lines

    assert part1(example()) == 143
    assert part2(example()) == 123

    print(f'Part 1: {part1(fetch_lines(year=2024, day=5))}')
    print(f'Part 2: {part2(fetch_lines(year=2024, day=5))}')
