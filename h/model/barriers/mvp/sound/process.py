import math
from time import sleep

from model.barriers.mvp.sound.cpu import CPU


class Process:

    def __init__(self, beeps):
        self.dataset = None
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
            "c": 3,
        }
        self.scheme_protect = {}
        for schem in self.scheme:
            self.scheme_protect[schem] = 1 + self.scheme[schem] + 1
        self.dimension = sum(self.scheme.values())


    def main(self):
        self.cpu = {}
        self.res = {}
        self.ending = ""
        for index in self.scheme:
            self.cpu[index] = CPU(n=self.scheme_protect[index])
            self.res[index] = []

        self.raw_file = open("input.raw.txt", mode="rb")
        while True:
            self.process()
            break
        self.raw_file.close()

    def process(self):
        for seek in range(1, self.dimension + 1):
            # self.dataset = self.get_data()
            self.dataset = self.get_data_all()
            self.process_dataset(seek=seek)

    def process_dataset(self, seek):
        print(self.res)
        for chunk in self.dataset:
            for index, raw in chunk.items():
                results = self.cpu[index].get(raw=raw, seek=seek)
                uniq, summa = self.get_uniq(results)
                self.res[index].append(uniq)
                print(
                    f"seek={str(seek).rjust(2, ' ')} | " +
                    f"raw={str(raw).rjust(max(self.scheme.values()), ' ')} | " +
                    f"summa={str(summa).rjust(4, ' ')} " +
                    f"{self.res[index][-1]}"
                )
                assert len(self.res[index]) == len(set(self.res[index]))

    def get_data_all(self) -> list:
        dataset = []
        for index in self.scheme:
            for data in range(2 ** self.scheme[index]):
                raw = f"{data:{self.scheme[index]}b}". \
                    replace(' ', '0')
                dataset.append({index: raw})
        return dataset

    def get_data(self) -> list:
        dataset = []
        dim = self.dimension - len(self.ending)
        count_bytes = dim // 8
        if dim % 8 != 0:
            dim += 1
        data = self.raw_file.read(count_bytes)
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


                # hz = summa
                # duration = 1 / (math.pi ** 2 * 2 ** self.dimension - hz)
                # duration = duration * 2 ** seek
                # print(duration)
                # self.beeps.play(frequency=hz)
                # sleep(duration)
                # self.beeps.stop(0)
                # for i in range(1, len(result_list)):
                #     print(
                #      f"time={time} | data={data} | " +
                #      f"hz={result_list[i][0]} | duration={result_list[i][1]}"
                #     )
                #     sleep(result_list[i][1] - result_list[i-1][1])
                #     self.beeps.stop(0)

