
class CPU:

    def __init__(self, n: int, limit: int = 1):
        self.raw = None
        self.seek = None
        self.limit = limit
        self.n = n
        self.lenght = self.n - 2
        self.freq_curr = [
            round(self.limit * 2 ** (i / self.n))
            for i in range(1, self.n - 1)
        ]
        self.freq_limit = self.freq_curr[:]
        self.input = [0] * self.lenght

    def get(self, raw: str, seek: int) -> list:
        self.raw = raw[::-1]
        self.seek = seek
        return self.process()

    def check(self, results: list) -> bool:
        recovery = self.anti_process(
            results=results,
        )
        return recovery == self.raw

    def value2input(self):
        i = 0
        for digit in self.raw:
            self.input[i] = -1 if int(digit) == 0 else 1
            i += 1

    def freq2statepos(self):
        positions = []
        states = self.input[:]
        for f in range(len(self.freq_curr)):
            pos = self.freq_curr[f]
            direction = 1
            t = self.seek
            while t > 0:
                if states[f] <= -self.n:
                    direction = 1
                elif states[f] >= self.n:
                    direction = -1
                states[f] += direction
                pos += direction
                t -= 1
            positions.append(pos)
        return states, positions

    def process(self) -> list:
        self.value2input()
        states, positions = self.freq2statepos()
        results = []
        for i in range(len(self.input)):
            result = []
            for f in range(len(self.freq_limit)):
                result.append(self.input[i] * states[f])
            results.append({positions[i]:  result})
        return results

    def anti_process(self, results: list) -> int:
        return len(results)
