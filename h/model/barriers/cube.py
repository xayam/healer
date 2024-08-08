import sys
from typing import Tuple

from model.barriers.router import paths_paths


def cube_get(olap, indexes, key: int) -> int:
    return key


def cube_put(key, value) -> bool:
    return True


def cube_indexes(width) -> Tuple[list, list]:
    buffer = []
    # limit = key_limit(name)
    # sys.exit()
    for name in list(range(1, width)):
        paths = paths_paths(width=name, verbose=0)
        # print(name)
        # print(paths)
        buffer.append(paths[-1])
    olap = []
    indexes = []
    for i in range(1, len(buffer)):
        row = "".join(['1' for _ in range(1, i + 1)])
        row = row.rjust(width - 1, '0')
        index = row.find('1')
        olap.append(row)
        indexes.append(index)
    olap = ["".join(['0'] * (width - 1))] + olap
    indexes = [width - 1] + indexes

    print("\n".join(olap))
    print(indexes)
    sys.exit()

    return olap, indexes
