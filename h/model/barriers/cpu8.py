import math


class CPU8:
    n = 5

    def __init__(self, limit):
        self.freq = [
            round(limit * 2 ** (i / self.n))
            for i in range(0, self.n + 1)
        ]
        self.state = {freq: 0 for freq in range(limit, 2 * limit + 1)}

    def get(self, key, pos):
        return self.process(value=key, time=pos)

    def process(self, value, time):

        return 0