import math
import random
from typing import Tuple

import winsound


class CPU8:
    n = 5

    def __init__(self, limit):
        self.limit = limit
        self.freq = [
            round(self.limit * 2 ** (i / self.n))
            for i in range(0, self.n + 1)
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
        s = f"{value:8b}".replace(" ", "0")
        i = 0
        for c in s:
            self.input[i] = -1 if int(c) == 0 else 1
            i += 1
        positions = []
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
            self.state[pos] = 1
            positions.append(pos)
            self.freq[f] = pos
        result = self.input[0] * \
                 self.input[1] * \
                 self.state[positions[1] - self.limit]
        result *= self.input[2] * \
                  self.input[3] * \
                  self.state[positions[2] - self.limit]
        result *= self.input[4] * \
                  self.input[5] * \
                  self.state[positions[3] - self.limit]
        result *= self.input[6] * \
                  self.input[7] * \
                  self.state[positions[4] - self.limit]
        result *= self.state[positions[0] - self.limit] * \
                  self.state[positions[-1] - self.limit]
        self.clear()
        return result, positions

if __name__ == "__main__":
    limits = [216 * 2 ** i for i in range(6)]
    cpus = []
    for limit in limits:
        cpus.append(CPU8(limit=limit))
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
                rs, ps = cpu.get(raw=data, seek=time)
                print(f"time={time} | raw={data} | result={rs}")
                if rs == 1:
                    for hz in ps:
                        winsound.Beep(hz, 2)
                        hzs.append(hz)
            else:
                break
            data = raw_file.read(1)
        time += 1
    raw_file.close()
