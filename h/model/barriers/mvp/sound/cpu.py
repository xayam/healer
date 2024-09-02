from typing import Tuple


class CPU:

    def __init__(self, n: int, limit: int = 1):
        self.limit = limit
        self.n = n
        self.lenght = self.n - 2
        self.freq_curr = [
            round(self.limit * 2 ** (i / self.n))
            for i in range(1, self.n - 1)
        ]
        self.freq_limit = self.freq_curr[:]
        self.input = [0] * self.lenght

    def get(self, raw: int, seek: int) -> list:
        return self.process(value=raw, time=seek)

    def process(self, value: int, time: int) -> list:
        s = f"{value:{self.lenght}b}".replace(" ", "0")
        i = 0
        # print(s)
        for c in s:
            # print(i)
            self.input[i] = -1 if int(c) == 0 else 1
            i += 1
        positions = []
        states = self.input
        for f in range(len(self.freq_curr)):
            pos = self.freq_curr[f]
            direction = 1
            t = time
            while t > 0:
                if states[f] <= -self.n:
                    direction = 1
                elif states[f] >= self.n:
                    direction = -1
                states[f] += direction
                pos += direction
                t -= 1
            positions.append(pos)
        results = []
        for i in range(len(self.input)):
            result = []
            for f in range(len(self.freq_limit)):
                result.append(self.input[i] * states[f])
            results.append({positions[i]:  result})
        return results
