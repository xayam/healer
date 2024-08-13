import math

from model.utils import utils_beep


def key_get(name: int, number: int) -> int:
    # name = utils_convert_base(name, level, 10)
    # new_width = int(name, level)
    # print(new_width)
    # key_limit(new_width)
    # while new_width > level:
    #     new_width -= level
    # new_width += level + level
    # new_data = data[:new_width]
    # return new_width, new_data, data[new_width:]
    value = 1
    return value


def key_limit(width=32) -> int:
    assert width > 0
    limit = width
    while True:
        old_limit = limit
        limit = 4 * math.ceil(math.log2(limit)) + 2
        # print(limit)
        if limit == old_limit:
            break
        utils_beep(limit)
    return limit
