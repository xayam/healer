import math
import pprint
import random
import sys

from typing import Tuple

from model import *
from model.utils import beep, convert_base


# import sys
# from functools import reduce


def zero_limit(width=32) -> int:
    assert width > 0
    limit = width
    while True:
        old_limit = limit
        limit = 4 * math.ceil(math.log2(limit)) + 2
        if limit == old_limit:
            break
        beep(limit)
    return limit


def zero_get_path_by_name(name: int = 0, width: int = 32) -> list:
    limit = zero_limit(width)
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
        beep(destination)
    return paths


def zero_get_new_name(old_name: int, width=32) -> list:
    # beep(old_name)
    return [old_name] + zero_get_path_by_name(old_name, width)


def zero_paths(name: int = 0, width: int = 32, verbose=0) -> list:
    assert width > 0
    assert 0 <= name <= width
    result = []
    if name == 0:
        for i in range(width):
            # beep(i)
            paths = zero_get_new_name(i)
            len_paths = len(paths)
            len_set_paths = len(set(paths))
            assert len_paths - len_set_paths == 1
            result.append(paths)
        if verbose > 0:
            pprint.pprint(result)
        return result
    else:
        # beep(key)
        paths = zero_get_new_name(name)
        len_paths = len(paths)
        len_set_paths = len(set(paths))
        if verbose > 0:
            print(paths, len_paths, len_set_paths)
        assert len_paths - len_set_paths == 1
        return result + paths


def zero_olap_indexes() -> Tuple[list, list]:
    name = 1
    buffer = []
    limit = zero_limit(name)
    for name in list(range(1, limit)) + list(range(name + 1, limit, -1)):
        paths = zero_paths(width=name, verbose=0)
        buffer.append(paths[-1])
    for i in range(len(buffer)):
        buffer[i] = [0] * (7 - len(buffer[i])) + buffer[i]
        for j in range(len(buffer[i])):
            buffer[i][j] = "".join((['0000000'] * 6 + [f"{buffer[i][j]:7b}".replace(' ', '0')]))
        buffer[i] = "".join(buffer[i])
    olap = []
    indexes = []
    for i in range(len(buffer)):
        row = "".join(buffer[i])
        index = row.find('1')
        if index < 0:
            continue
        olap.append(row)
        index = 7 ** 3 - index - 1
        indexes.append(index)
    olap[-1] = '0' * (7 ** 3 - 5) + '11011'
    olap = ['0' * (7 ** 3)] + olap
    indexes = [1] + indexes
    return olap, indexes


def zero_return(width: int, data: str, number: int):
    width = convert_base(width, number, 10)
    new_width = int(width, number)
    print(new_width)
    zero_limit(new_width)
    while new_width > number:
        new_width -= number
    new_width += number + number
    new_data = data[:new_width]
    return new_width, new_data, data[new_width:]


def zero_get_olap_destination(olap, indexes, name: int) -> int:
    return name


def zero_put_olap(key, value) -> bool:
    return True


def main() -> bool:
    olap, indexes = zero_olap_indexes()
    variants = [variant for variant in range(23, 1025)]
    while True:
        key = random.choice(variants)
        variants.__delitem__(key)
        value = zero_get_olap_destination(olap=olap, indexes=indexes, name=key)
        success = zero_put_olap(key, value)
        if not variants:
            break
    return success

if __name__ == "__main__":
    main()
