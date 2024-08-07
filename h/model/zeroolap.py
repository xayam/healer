import math
import pprint
import sys
from functools import reduce

from model.utils import progress


def zero_limit(width=32) -> int:
    assert width > 0
    limit = width
    while True:
        old_limit = limit
        limit = 4 * math.ceil(math.log2(limit)) + 2
        if limit == old_limit:
            break
    return limit


def zero_get_path_by_name(name: int = 0, width: int = 32) -> list:
    limit = zero_limit(width)
    # print(limit)
    # sys.exit()
    # print(width, name)
    assert name >= 0
    passenger = name
    paths = [0]
    destination = passenger
    if passenger == 0:
        paths.append(limit)
        return paths
    else:
        if passenger == limit:
            pass
        else:
            paths = [destination]
    while True:
        destination = 4 * math.ceil(math.log2(destination)) + 2
        paths.append(destination)
        if destination == limit:
            break
    return paths


def zero_get_new_name(old_name: int, width=32) -> list:
    return [old_name] + zero_get_path_by_name(old_name, width)


def zero_paths(name: int = 0, width: int = 32, verbose=0) -> list:
    assert width > 0
    assert 0 <= name <= width
    result = []
    if name == 0:
        for i in range(width):
            paths = zero_get_new_name(i)
            len_paths = len(paths)
            len_set_paths = len(set(paths))
            assert len_paths - len_set_paths == 1
            result.append(paths)
        if verbose > 0:
            pprint.pprint(result)
        return result
    else:
        paths = zero_get_new_name(name)
        len_paths = len(paths)
        len_set_paths = len(set(paths))
        if verbose > 0:
            print(paths, len_paths, len_set_paths)
        assert len_paths - len_set_paths == 1
        return result + paths


def main(width):
    result = []
    max_len = 0
    limit = zero_limit(width)
    for width in list(range(1, limit)) + list(range(width, limit, -1)):
        paths = zero_paths(width=width, verbose=0)
        result.append(paths[-1])
        len_result = len(result[-1])
        if len_result > max_len:
            max_len = len_result
    for i in range(len(result)):
        result[i] = [0] * (8 - len(result[i])) + result[i]
        for j in range(len(result[i])):
            x = result[i][j]
            result[i][j] = f"{x:8b}".replace(' ', '0')
    zero = '0' * 8
    limit_1 = limit - 1
    limit_1 = f"{limit_1:8b}".replace(' ', '0')
    limit = f"{limit:8b}".replace(' ', '0')
    result.append([zero, zero, zero, zero, zero, zero, limit_1, limit])
    res = [[]]
    for i in range(0, len(result)):
        res.append(result[i])
        for j in range(6):
            res.append([zero]*8)
    r = []
    for i in range(len(res)):
        r.append("".join(res[i]))

    pprint.pprint(r)
    print(len(result))
    print(r[-7:-6][0][-16:])
    return max_len


if __name__ == "__main__":
    count_of_passengers = 32
    main(width=count_of_passengers)
    # zero_paths(name=0, width=32)
