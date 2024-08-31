import functools
import math
import random
import sys
from typing import Tuple

import winsound


class CPU8:

    def __init__(self, limit, n):
        self.limit = limit
        self.n = n
        self.freq = [
            round(self.limit * 2 ** (i / self.n))
            for i in range(self.n + 1)
        ]
        self.input = []
        self.state = {}
        self.clear()

    def clear(self):
        self.input = [0] * 8
        self.state = {pos: -1 for pos in range(self.limit + 1)}

    def get(self, raw: int, seek: int) -> Tuple[int, list]:
        return self.process(value=raw, time=seek)

    def process(self, value: int, time: int) -> Tuple[int, list]:
        s = f"{value:8b}".replace(" ", "0")[::-1]
        i = 0
        for c in s:
            self.input[i] = -1 if int(c) == 0 else 1
            i += 1
        positions = []
        states = []
        for f in range(len(self.freq)):
            pos = self.freq[f]
            direction = -1
            t = time
            while t != 0:
                if pos == self.limit:
                    direction = 1
                    pos += direction
                    continue
                elif pos == 2 * self.limit:
                    direction = -1
                    pos += direction
                    continue
                pos += direction
                t -= 1
            self.state[pos - self.limit] = - self.state[pos - self.limit]
            positions.append(pos)
            states.append(self.state[pos - self.limit])
            self.freq[f] = pos
        result1 = self.input[0] * self.input[1] * states[1]
        result2 = self.input[2] * self.input[3] * states[2]
        result3 = self.input[4] * self.input[5] * states[3]
        result4 = self.input[6] * self.input[7] * states[4]
        result1 = (result1 + result2) * states[0]
        result2 = (result3 + result4) * states[5]
        result = result1 + result2
        # sys.exit()
        self.clear()
        return result, positions


if __name__ == "__main__":
    n = 5
    limits = [216 * 2 ** i for i in range(6)]
    cpus = []
    for limit in limits:
        cpus.append(CPU8(limit=limit, n=n))
    rnd = random.SystemRandom(0)
    hzs = []
    raw_file = open("raw.zip", mode="rb")
    data = raw_file.read(1)
    time = 0
    while data:
        for cpu in cpus:
            # data = rnd.choice(list(range(256)))
            if data:
                data = int.from_bytes(data, byteorder="big")
                rs, gzs = cpu.get(raw=data, seek=time)
                if rs > 0:
                    gz = sum(gzs) / len(gzs)
                    print(f"time={time} | raw={data} | gzs={gzs} | rs={rs}")
                    if max(gzs) == min(gzs):
                        duration = 0.1
                    else:
                        duration = (max(gzs) - gz) / (max(gzs) - min(gzs))
                    # print(gz, duration)
                    # sys.exit()
                    winsound.Beep(round(gz), round(25 * duration) + 1)
            else:
                break
            data = raw_file.read(1)
        time += 1
    raw_file.close()
