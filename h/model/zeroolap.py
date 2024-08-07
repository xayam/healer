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


def main(maximum: int):
    result = []
    max_len = 0
    for width in range(1, 23):
        paths = zero_paths(width=width, verbose=0)
        result.append(paths[-1][1:])
        len_result = len(result[-1])
        if len_result > max_len:
            max_len = len_result
        progress(f"{width}/{maximum}, {len(result)}, {max_len}, {width/maximum}% ")
    pprint.pprint(result)
    assert len(result) == maximum - 1
    print(maximum, len(result), len(result[1]))




if __name__ == "__main__":
    for m in range(2**32, 2**32+1):
        main(maximum=m)

    # zero_paths(name=0, width=32)
