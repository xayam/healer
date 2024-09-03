import math
from time import sleep


class CPU:

    def __init__(self, n: int, limit: int = 1, beeps = None):
        self.results_old = []
        self.results = []
        self.beeps = beeps
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

    def get(self, raw: str, seek: int, mute: bool = True) -> list:
        self.raw = raw[::-1]
        self.seek = seek
        self.results_old = self.results[:]
        self.results = self.process()
        if not mute and self.results_old:
            self.say()
        return self.results

    def check(self, results: list) -> bool:
        recovery = self.anti_process(
            results=results,
        )
        return recovery == self.raw

    def say(self):
        # print(self.results_old)
        # print(self.results)
        hz = self.collision()
        # hz = math.pi ** 2 * 2 ** self.lenght - hz
        # duration = 1 / hz
        # duration = duration * 2 ** self.seek
        # hz = round(hz)
        # print(hz)
        # print(duration)
        self.beeps.play(frequency=hz)
        sleep(0.022)
        self.beeps.stop(0)

    def collision(self) -> int:
        result = []
        summa = 0
        for index in range(len(self.results_old)):
            arr = []
            key, value = list(self.results[index].items())[0]
            key_old, value_old = list(self.results_old[index].items())[0]
            for i in range(len(value)):
                delta = value[i] - value_old[i]
                summa += abs(delta)
                arr.append(delta)
            result.append({key - key_old: arr})
        return summa


    def raw2input(self):
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
        self.raw2input()
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
