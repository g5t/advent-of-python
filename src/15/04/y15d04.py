def md5hashhex(value: str) -> str:
    from hashlib import md5
    hasher = md5()
    hasher.update(value.encode())
    return hasher.hexdigest()


def find_first_hash_with_n_leading_zeros(key: str, n) -> int:
    for i in range(10**7):
        if md5hashhex(f'{key}{i}').startswith('0'*n):
            return i
    return -1


def part(key: str, n: int = 5):
    value = find_first_hash_with_n_leading_zeros(key, n)
    if value < 0:
        raise ValueError('No such hash found. Increase search range?')
    print(value)


if __name__ == '__main__':
    from faoci.interface import fetch_lines
    assert find_first_hash_with_n_leading_zeros('abcdef', 5) == 609043
    assert find_first_hash_with_n_leading_zeros('pqrstuv', 5) == 1048970
    part(fetch_lines(year=2015, day=4)[0])
    part(fetch_lines(year=2015, day=4)[0], 6)
