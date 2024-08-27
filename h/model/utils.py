import math
import sys
import colorama
import winsound


def utils_progress(message: str) -> None:
    sys.stdout.write("\r" + message)
    sys.stdout.flush()


def utils_print(*args, separator=" ") -> None:
    sys.stdout.write(separator.join(map(str, args)))
    sys.stdout.write("\n")
    sys.stdout.flush()


def utils_colorize_bool(data: bool) -> str:
    message = colorama.Fore.BLACK
    if data:
        message += colorama.Back.GREEN + f"{data} "
    else:
        message += colorama.Back.RED + f"{data}"
    message += colorama.Style.RESET_ALL
    return message


def utils_colorize(data) -> str:
    message = colorama.Fore.BLACK
    message += colorama.Back.RED + f"{data}"
    message += colorama.Style.RESET_ALL
    return message


def utils_colorize_swap(data: list, from_pos: int, to_pos: int) -> str:
    message = ""
    position = 0
    for d in data:
        if position in [from_pos, to_pos]:
            message += utils_colorize(d)
        else:
            message += str(d)
        position += 1
    return message


def utils_list_to_str(data: list) -> str:
    return "".join(map(str, data))


def utils_get_sum_width(width: int) -> float:
    summa = 0
    for x in range(1, math.ceil(math.log2(width + 1))):
        summa += math.log2(x + 1)
    return summa


def utils_convert_base(num, to_base=10, from_base=10):
    if isinstance(num, str):
        n = int(num, from_base)
    else:
        n = int(num)
    # now convert decimal to 'to_base' base
    alphabet = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ"
    if n < to_base:
        return alphabet[n]
    else:
        return utils_convert_base(n // to_base, to_base) + alphabet[n % to_base]


def utils_beep(freq, direction=2, verbose=1):
    direction = freq
    if freq > 36:
        if verbose > 0:
            print(f"freq={freq}, direction={direction}")
        winsound.Beep(freq, duration=direction)
