import math
from time import sleep

from model.barriers.mvp.sound.cpu import CPU


class Process:

    def __init__(self, beeps):
        self.dataset = []
        self.cpu = None
        self.res = None
        self.ending = None
        self.raw_file = None
        self.beeps = beeps
        self.scheme = {
            # "x": 16, "y": 16, "z": 16,
            # "r": 8,
            # "g": 4,
            # "b": 4,
            "c": 8,
        }
        self.scheme_protect = {}
        for schem in self.scheme:
            self.scheme_protect[schem] = 1 + self.scheme[schem] + 1
        self.dimension = sum(self.scheme.values())

    def init(self):
        self.cpu = {}
        self.res = {}
        self.ending = ""
        for index in self.scheme:
            self.cpu[index] = CPU(
                n=self.scheme_protect[index],
                limit=1,
                beeps=self.beeps
            )
            self.res[index] = []

    def main(self):
        self.init()
        self.raw_file = open("input.raw.txt", mode="rb")
        seek = 1
        while self.dataset is not None:
            self.process(seek)
            seek += 1
        self.raw_file.close()

    def process(self, seek):
        self.dataset = self.get_data()
        # self.dataset = self.get_data_all()
        self.process_dataset(seek=seek)

    def process_dataset(self, seek):
        for chunk in self.dataset:
            self.process_step(chunk, seek)

    def process_step(self, chunk, seek):
        for index, raw in chunk.items():
            results = self.cpu[index].get(
                raw=raw, seek=seek, mute=False,
            )
            uniq, summa = self.get_uniq(results)
            self.res[index].append(uniq)
            print(
                f"seek={str(seek).rjust(2, ' ')} | " +
                f"raw={str(raw).rjust(max(self.scheme.values()), ' ')} | " +
                f"summa={str(summa).rjust(4, ' ')} "
                + f"{self.res[index][-1]}"
            )
            # assert len(self.res[index]) == len(set(self.res[index]))

    def get_data_all(self) -> list:
        dataset = []
        for index in self.scheme:
            for data in range(2 ** self.scheme[index]):
                raw = f"{data:{self.scheme[index]}b}". \
                    replace(' ', '0')
                dataset.append({index: raw})
        return dataset

    def get_data(self):
        dataset = []
        dim = self.dimension - len(self.ending)
        count_bytes = dim // 8
        if dim % 8 != 0:
            dim += 1
        data = self.raw_file.read(count_bytes)
        if not data:
            return None
        data = int.from_bytes(data, byteorder="big")
        data = f"{data:{8 * count_bytes}b}".replace(' ', '0')
        data = self.ending + data
        start = 0
        for index in self.scheme:
            raw = data[start:start + self.scheme[index]]
            raw = raw.rjust(self.scheme[index], '0')
            dataset.append({index: raw})
            start += self.scheme[index]
        self.ending = data[start:]
        return dataset

    @staticmethod
    def get_uniq(results):
        uniq = ""
        summa = 0
        for i in range(len(results)):
            for key, value in results[i].items():
                buffer = []
                for v in value:
                    buffer.append(key + v)
                uniq += "|>" + str(key).rjust(1, ' ') + \
                        "<|" + "|".join(
                    map(lambda x: str(x).rjust(
                        2, ' '),
                        value))
                summa += sum(buffer)
        return uniq, summa
