import math
import pprint
import sys
from functools import reduce
from time import sleep

import winsound

from model.utils import progress, convert_base


def zero_limit(width=32) -> int:
    assert width > 0
    limit = width
    while True:
        old_limit = limit
        limit = 4 * math.ceil(math.log2(limit)) + 2
        if limit == old_limit:
            break
        if limit > 36:
            print(limit)
            winsound.Beep(limit, 2)
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
        if destination > 36:
            print(destination)
            winsound.Beep(destination, 2)
    return paths


def zero_get_new_name(old_name: int, width=32) -> list:
    if old_name > 36:
        print(old_name)
        winsound.Beep(old_name, 2)
    return [old_name] + zero_get_path_by_name(old_name, width)


def zero_paths(name: int = 0, width: int = 32, verbose=0) -> list:
    assert width > 0
    assert 0 <= name <= width
    result = []
    if name == 0:
        for i in range(width):
            if i > 36:
                print(i)
                winsound.Beep(i, 2)
            paths = zero_get_new_name(i)
            len_paths = len(paths)
            len_set_paths = len(set(paths))
            assert len_paths - len_set_paths == 1
            result.append(paths)
        if verbose > 0:
            pprint.pprint(result)
        return result
    else:
        if name > 36:
            print(name)
            winsound.Beep(name, 2)
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
    if width > 36:
        print(width)
        winsound.Beep(width, 2)
    limit = zero_limit(width)
    for width in list(range(1, limit)) + list(range(width, limit, -1)):
        if width > 36:
            print(width)
            winsound.Beep(width, 2)
        paths = zero_paths(width=width, verbose=0)
        result.append(paths[-1])
        len_result = len(result[-1])
        if len_result > max_len:
            max_len = len_result
    for i in range(len(result)):
        result[i] = [0] * (2 - len(result[i])) + result[i]
        for j in range(len(result[i])):
            x = f"{result[i][j]:2b}".replace(' ', '0')
            result[i][j] = "".join((['00'] * 1 + [x]))
        result[i] = "".join(result[i])
    # pprint.pprint(result)
    # sys.exit()
    r = []
    for i in range(0, len(result)):
        s = "".join(result[i])
        index = s.find('1')
        r.append(s)
        index = 7 ** 3 - index - 1
        for j in range(index):
            r.append("".join((['0'] * (7 ** 3))))
    # print(r)
    # sys.exit()
    return len(r), r


def zero_compress(width: int, data: str, number: int):
    width = convert_base(width, 6, 10)
    new_width = int(width, 6)
    print(new_width)
    while new_width > 0:
        if new_width > 36:
            print(new_width)
            winsound.Beep(new_width, 2)
        # sleep(i/(7*3))
        # print(dsc)
        # print(new_width)
        new_width -= 6
    new_width += 6 + number
    new_data = data[:new_width]
    return new_width, new_data, data[new_width:]

if __name__ == "__main__":

    count_of_passengers = 1
    print(count_of_passengers)
    number = 1
    while True:
        lr1, r1 = extension(width=count_of_passengers)
        # pprint.pprint(r1)
        print(lr1)
        # break
        _, new_data, _ = zero_compress(width=lr1, data="".join(r1), number=number)
        print(number, len(new_data))
        number += 1
        count_of_passengers = len(new_data)

    # zero_paths(name=0, width=32)
