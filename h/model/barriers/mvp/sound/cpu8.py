from typing import Tuple


class CPU8:

    def __init__(self, limit, n):
        self.limit = limit
        self.n = n
        self.freq_curr = [
            round(self.limit * 2 ** (i / self.n))
            for i in range(self.n + 1)
        ]
        self.freq_limit = self.freq_curr[:]
        self.input = []
        self.state = {}
        self.clear()

    def clear(self):
        self.input = [0] * 8
        self.freq_curr = self.freq_limit[:]
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
        pos_states = []
        states = [-7, -5, -3, -1, 1, 3, 5, 7]
        directions = [1, -1, 1, -1, 1, -1, 1, -1]
        for f in range(1, len(self.freq_curr) - 1):
            pos = self.freq_curr[f]
            direction = directions[f]
            t = time
            while t > 0:
                if states[f] <= -self.n:
                    direction = -direction
                elif states[f] >= self.n:
                    direction = -direction
                pos += states[f]
                states[f] += direction
                t -= 1
            self.state[pos - self.limit] = - self.state[pos - self.limit]
            positions.append(pos)
            pos_states.append(self.state[pos - self.limit])
            self.freq_curr[f] = pos
        result = []
        for i in range(len(self.input)):
            result.append(self.input[i] * states[i])
        return sum(result), positions
