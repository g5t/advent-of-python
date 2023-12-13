def day_script(year: int, day: int):
    from textwrap import dedent
    return dedent(f"""\
    # Path: {year:02d}/{day:02d}/y{year:02d}d{day:02d}.py
    # Puzzle Source: https://adventofcode.com/{year}/day/{day}
    
    from pathlib import Path
    def get_lines(filename):
        if isinstance(filename, str):
            filename = Path(filename)
        filename = filename.resolve()
        if not filename.exists():
            return []
            
        with open(filename, 'r') as file:
            return file.read().splitlines()
    
    
    def part1(lines: list[str]) -> int:
        return len(lines)
        
        
    def part2(lines: list[str]) -> int:
        return len(lines)
            
    
    if __name__ == '__main__':
        from faoci.interface import fetch_lines
        
        assert part1(get_lines('y{year:02d}d{day:02d}.test')) == 1
        
        lines = fetch_lines(year={year}, day={day})
        print(f'Part 1: {{part1(lines)}}')
        print(f'Part 2: {{part2(lines)}}')
    
    """)


def setup_day(*, year: int, day: int, root: str, quiet: bool):
    from pathlib import Path
    root = Path(root).resolve()
    if not root.exists():
        raise RuntimeError(f"Root directory {root} does not exist")
    if not root.is_dir():
        raise RuntimeError(f"Root directory {root} is not a directory")
    # make the year directory if it doesn't exist
    year_dir = root.joinpath(f'{year % 1000:02d}')
    # make the day directory if it doesn't exist
    day_dir = year_dir.joinpath(f'{day:02d}')
    if not day_dir.exists():
        day_dir.mkdir(parents=True)
    # write out a basic day script
    with open(day_dir.joinpath(f'y{year:02d}d{day:02d}.py'), 'w') as file:
        file.write(day_script(year, day))
    # write out a basic test file
    with open(day_dir.joinpath(f'y{year:02d}d{day:02d}.test'), 'w') as file:
        file.write('')


if __name__ == '__main__':
    from argparse import ArgumentParser
    parser = ArgumentParser(description='Setup a new day for Advent of Code')
    parser.add_argument('-y', '--year', type=int, help='the year to setup', default=None)
    parser.add_argument('-d', '--day', type=int, help='the day of advent to setup', default=None)
    parser.add_argument('-q', '--quiet', action='store_true', help='quiet operation')
    parser.add_argument('-r', '--root', type=str, help='the root directory to setup in', default=None)
    args = parser.parse_args()

    if args.year is None:
        from datetime import datetime
        args.year = datetime.now().year
    if args.day is None:
        from datetime import datetime
        args.day = datetime.now().day
    if args.root is None:
        args.root = '.'

    setup_day(year=args.year, day=args.day, root=args.root, quiet=args.quiet)
