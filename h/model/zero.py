from time import sleep
from typing import Tuple

from model.barriers.key import key_get
from model.barriers.cube import cube_get, cube_put, cube_indexes
from model.barriers.router import paths_path_get, route_level_up


def zero_rename(old_name: int, width=32) -> list:
    return [old_name] + paths_path_get(old_name, width)


def zero_i_want_to_come_back(olap, indexes,
                             name: int, level: int) -> Tuple[bool, int, list]:
    key = key_get(name, level)
    value = cube_get(olap=olap, indexes=indexes, key=key)
    you_can_back, error, route = cube_put(key, value)
    return you_can_back, error, route


def zero_test(width):
    olap, indexes = cube_indexes(width=width)
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
            name = route_level_up(name)
            level += 1


if __name__ == "__main__":
    zero_test(width=11 + 1)
