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
        self.state = {}
        self.clear()

    def clear(self):
        self.input = [0] * 8
        self.freq_curr = self.freq_limit[:]
        self.state = {pos: -1 for pos in range(self.limit + 1)}

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
        result_states = []
        directions = [1, -1, 1, -1, 1, -1, 1, -1]
        for f in range(len(self.freq_curr)):
            pos = self.freq_curr[f]
            states = [-7, -5, -3, -1, 1, 3, 5, 7]
            direction = directions[f]
            t = time
            while t > 0:
                if states[f] <= -self.n:
                    direction = -direction
                elif states[f] >= self.n:
                    direction = -direction
                states[f] += direction
                pos += states[f]
                t -= 1
            result_states.append(states)
            positions.append(pos)
            self.freq_curr[f] = pos
        results = []
        table = {-6: 1, -4: 2, -2: 3, 0: 4, 2: 5, 4: 6, 6: 7}
        for i in range(len(self.input)):
            result = []
            for f in range(len(self.freq_limit)):
                result.append(self.input[i] * result_states[i][f])
            result = table[sum(result)]
            results.append({"hz": positions[i], "duration": result})
        results = sorted(results, key=lambda x: x["duration"])
        return results
