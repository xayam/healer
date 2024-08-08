import math
import pprint

from model.barriers.key import key_limit


def route_level_up(name, width):
    level = 0
    buffer = name
    while type(buffer) is list:
        buffer = buffer[0]
        level += 1
    if level >= width:
        return [buffer]
    else:
        return [buffer] * (width - level)



def paths_path_get(name: int = 0, width: int = 32) -> list:
    limit = key_limit(width)
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


def paths_paths(name: int = 1, width: int = 32, verbose=0) -> list:
    assert width > 0
    assert 1 <= name <= width
    result = []
    paths = route_level_up(name, width)
    if verbose > 0:
        pprint.pprint(paths)
    return paths
