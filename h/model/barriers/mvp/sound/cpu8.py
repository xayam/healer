from typing import Tuple


class CPU8:

    def __init__(self, limit, n):
        self.limit = limit
        self.n = n
        self.freq_curr = [
            round(self.limit * 2 ** (i / self.n))
            for i in range(1, self.n - 1)
        ]
        self.freq_limit = self.freq_curr[:]
        self.input = []
        # self.state = {}
        self.clear()

    def clear(self):
        self.input = [0] * 8
        self.freq_curr = self.freq_limit[:]
        # self.state = {pos: -1 for pos in range(self.limit + 1)}

    def get(self, raw: int, seek: int) -> list:
        return self.process(value=raw, time=seek)

    def process(self, value: int, time: int) -> list:
        s = f"{value:8b}".replace(" ", "0")[::-1]
        i = 0
        for c in s:
            self.input[i] = -1 if int(c) == 0 else 1
            i += 1
        # pos_states = []
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
            # print(positions[i] + sum(result), result)
            results.append({positions[i]:  result})
        # results = sorted(results.items(), key=lambda x: x[1])
        return results
