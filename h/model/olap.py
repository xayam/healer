import sys
from typing import Tuple

from model.key import key_limit
from model.paths import paths_paths


def olap_get(olap, indexes, key: int) -> int:
    return key


def olap_put(key, value) -> bool:
    return True


def olap_indexes(width) -> Tuple[list, list]:
    name = 1
    buffer = []
    limit = key_limit(name)
    for name in list(range(1, limit)) + list(range(name + 1, limit, -1)):
        paths = paths_paths(width=name, verbose=0)
        buffer.append(paths[-1])
    for i in range(len(buffer)):
        buffer[i] = [0] * (width - len(buffer[i])) + buffer[i]
        for j in range(len(buffer[i])):
            buffer[i][j] = "".join((['0'] * (width - 1) +
                                    [f"{buffer[i][j]:{width}b}".
                                    replace(' ', '0')]))
        buffer[i] = "".join(buffer[i])
    olap = []
    indexes = []
    for i in range(len(buffer)):
        row = "".join(buffer[i])
        index = row.find('1')
        if index < 0:
            continue
        olap.append(row)
        index = width ** 3 - index - 1
        indexes.append(index)
    olap[-1] = '0' * (width ** 3 - 5) + '11011'
    olap = ['0' * (width ** 3)] + olap
    indexes = [1] + indexes

    print("\n".join(olap))
    print(indexes)
    sys.exit()

    return olap, indexes
