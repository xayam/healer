import math


class CPU8:
    n = 5

    def __init__(self, limit):
        self.limit = limit
        self.freq = [
            round(self.limit * 2 ** (i / self.n))
            for i in range(0, self.n + 1)
        ]
        self.input = [0] * 8
        self.state = {pos: -1 for pos in range(self.limit + 1)}

    def get(self, raw, pos):
        return self.process(value=raw, time=pos)

    def process(self, value: int, time: int):
        s = f"{value}:8b".rjust(8, "0")
        i = 0
        for c in s:
            self.input[i] = -1 if int(c) == 0 else 1
            i += 1
        for freq in self.freq:
            pos = freq
            direction = -1
            t = time
            while t != 0:
                if pos == self.limit:
                    direction = 1
                    continue
                elif pos == 2 * self.limit:
                    direction = -1
                    continue
                pos += direction
                t -= 1
            self.state[pos] = 1
        result = self.input[0] * \
                 self.input[1] * \
                 self.state[self.freq[1] - self.limit]
        result *= self.input[2] * \
                  self.input[3] * \
                  self.state[self.freq[2] - self.limit]
        result *= self.input[4] * \
                  self.input[5] * \
                  self.state[self.freq[3] - self.limit]
        result *= self.input[6] * \
                  self.input[7] * \
                  self.state[self.freq[4] - self.limit]
        result *= self.state[self.freq[0] - self.limit] * \
                  self.state[self.freq[-1] - self.limit]
        return result