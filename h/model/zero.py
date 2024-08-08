import math
from time import sleep
from typing import Tuple

from model.olap import olap_get, olap_put, olap_indexes
from model.paths import paths_path_get
from model.utils import beep


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


def zero_rename(old_name: int, width=32) -> list:
    return [old_name] + paths_path_get(old_name, width)


def zero_key_get(name: int, number: int) -> int:
    # name = convert_base(name, level, 10)
    # new_width = int(name, level)
    # print(new_width)
    # zero_limit(new_width)
    # while new_width > level:
    #     new_width -= level
    # new_width += level + level
    # new_data = data[:new_width]
    # return new_width, new_data, data[new_width:]
    value = 1
    return value


def zero_i_want_to_come_back(olap, indexes,
                             name: int, level: int) -> Tuple[bool, int, list]:
    key = zero_key_get(name, level)
    value = olap_get(olap=olap, indexes=indexes, key=key)
    you_can_back, error, route = olap_put(key, value)
    return you_can_back, error, route


def main_test():
    olap, indexes = olap_indexes()
    level = 1
    name = 22 + 1
    while True:

        i_can_return, error, route = zero_i_want_to_come_back(
            olap=olap, indexes=indexes,
            name=name, level=level
        )
        if i_can_return and (error == 0):
            for target in route:
                if target == name:
                    sleep(level)
                    continue
                else:
                    name = target
                    # level -= 1
        else:
            name = zero_rename(name, name)
            level += 1


if __name__ == "__main__":
    main_test()
