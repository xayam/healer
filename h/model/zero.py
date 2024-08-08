from time import sleep
from typing import Tuple

from model.key import key_get
from model.olap import olap_get, olap_put, olap_indexes
from model.route import paths_path_get


def zero_rename(old_name: int, width=32) -> list:
    return [old_name] + paths_path_get(old_name, width)


def zero_i_want_to_come_back(olap, indexes,
                             name: int, level: int) -> Tuple[bool, int, list]:
    key = key_get(name, level)
    value = olap_get(olap=olap, indexes=indexes, key=key)
    you_can_back, error, route = olap_put(key, value)
    return you_can_back, error, route


def zero_test(width=8):
    olap, indexes = olap_indexes(width=width)
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
    zero_test(width=8)
