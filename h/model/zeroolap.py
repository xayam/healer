import math
import pprint

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
    beep(old_name)
    return [old_name] + zero_get_path_by_name(old_name, width)


def zero_paths(name: int = 0, width: int = 32, verbose=0) -> list:
    assert width > 0
    assert 0 <= name <= width
    result = []
    if name == 0:
        for i in range(width):
            beep(i)
            paths = zero_get_new_name(i)
            len_paths = len(paths)
            len_set_paths = len(set(paths))
            assert len_paths - len_set_paths == 1
            result.append(paths)
        if verbose > 0:
            pprint.pprint(result)
        return result
    else:
        beep(name)
        paths = zero_get_new_name(name)
        len_paths = len(paths)
        len_set_paths = len(set(paths))
        if verbose > 0:
            print(paths, len_paths, len_set_paths)
        assert len_paths - len_set_paths == 1
        return result + paths


def extension(width):
    result = []
    max_len = 0
    beep(width)
    limit = zero_limit(width)
    for width in list(range(1, limit)) + list(range(width, limit, -1)):
        beep(width)
        paths = zero_paths(width=width, verbose=0)
        result.append(paths[-1])
        len_result = len(result[-1])
        if len_result > max_len:
            max_len = len_result
    for i in range(len(result)):
        beep(i)
        result[i] = [0] * (2 - len(result[i])) + result[i]
        for j in range(len(result[i])):
            beep(j)
            x = f"{result[i][j]:2b}".replace(' ', '0')
            result[i][j] = "".join((['00'] * 1 + [x]))
        result[i] = "".join(result[i])
    r = []
    for i in range(0, len(result)):
        beep(i)
        s = "".join(result[i])
        index = s.find('1')
        r.append(s)
        index = 7 ** 3 - index - 1
        for j in range(index):
            beep(index)
            r.append("".join((['0'] * (7 ** 3))))
    return len(r), r


def zero_compress(width: int, data: str, number: int):
    width = convert_base(width, 6, 10)
    new_width = int(width, 6)
    print(new_width)
    while new_width > 0:
        beep(new_width)
        new_width -= 6
    new_width += 6 + number
    new_data = data[:new_width]
    return new_width, new_data, data[new_width:]

if __name__ == "__main__":

    count_of_passengers = 1
    print(count_of_passengers)
    number = 1
    while True:
        beep(count_of_passengers)
        lr1, r1 = extension(width=count_of_passengers)

        _, new_data, _ = zero_compress(width=lr1, data="".join(r1), number=number)
        print(number, lr1, len(new_data))
        number += 1
        count_of_passengers = len(new_data)

    # zero_paths(name=0, width=32)
