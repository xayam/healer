import math
import random
import matplotlib.pyplot as plt
import threading
from time import sleep

import numpy
import pygame
from pygame.mixer import Sound, pre_init
from kivy.app import App
from kivy.uix.gridlayout import GridLayout
from kivy.clock import Clock
from kivy.core.window import Window

from model.barriers.mvp.sound.cpu import CPU

Window.size = (720, 400)


class Beep(Sound):

    def __init__(self, frequency, volume=.1):
        self.frequency = frequency
        pygame.mixer.Sound.__init__(self, self.build_samples())
        self.set_volume(volume)

    def build_samples(self):
        sample_rate = pygame.mixer.get_init()[0]
        period = int(round(sample_rate / self.frequency))
        amplitude = 2 ** (abs(pygame.mixer.get_init()[1]) - 1) - 1

        def frame_value(i):
            return amplitude * numpy.sin(
                2.0 * numpy.pi * self.frequency * i / sample_rate)

        return numpy.array([frame_value(x) for x in range(0, period)]).astype(
            numpy.int16)


class Beeps:

    def __init__(self):
        self.sounds = []
        self.frequency = []
        self.durations = []

    def stop(self, _):
        beep = self.sounds.pop(0)
        beep.stop()

    def play(self, frequency):
        self.sounds.append(Beep(frequency).play(-1))
        # Clock.schedule_once(
        #     callback=self.stop, timeout=dur
        # )


class ClockWidget(GridLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.beeps = Beeps()
        self.val = None
        self.ev = None
        self.ids.b1.bind(on_press=self.showtime)

    def countdown(self, dt):
        if self.val == 0:
            self.ids.l1.text = "Countdown Stopped"
            self.ids.l1.color = [1, 0, 0]
            self.ev.cancel()
            self.ids.b1.disabled = False
        else:
            self.ids.l1.text = "Current Value: {}".format(self.val)
            self.ids.l1.color = [1, 1, 1]
            self.val = self.val - 1

    def showtime(self, *args):
        thread = threading.Thread(target=self.main, args=[])
        thread.start()
        # self.val = int(self.ids.t1.text)
        self.ev = []
        self.ids.b1.disabled = True

    def main(self):
        bits = 11
        scheme = {
            # "x": 16, "y": 16, "z": 16,
            # "r": 8, "g": 8,
            "b": bits,
        }
        schemes = {i: 1 + scheme[i] + 1 for i in scheme}
        cpu = {}
        for i in schemes:
            # assert scheme[i] % 8 == 0
            cpu[i] = CPU(n=schemes[i])
        raw_file = open("input.raw.txt", mode="rb")
        r = []
        for tachyon in range(1, bits + 1):
            dataset = []
            for index in scheme:
                data = raw_file.read(scheme[index] // 8)
                data = int.from_bytes(data, byteorder="big")
                dataset.append({index: data})
            dataset = []
            for data in range(2 ** bits):
                dataset.append({"b": data})
            for chunk in dataset:
                for index, data in chunk.items():
                    uniq = ""
                    summa = 0
                    results = cpu[index].get(raw=data, seek=tachyon)
                    for i in range(len(results)):
                        for key, value in results[i].items():
                            # uniq += "|" + str(key).rjust(3, '0') + \
                            #          "|" + \
                            uniq += "".join(
                                map(lambda x: str(x).rjust(3, '0'), value)
                            )
                            summa += key + sum(value)
                    r.append(uniq)
                    print(
                        f"time={tachyon} | " +
                        f"data={str(data).rjust(3, ' ')} | " +
                        f"summa={str(summa).rjust(4, ' ')} | " +
                        f"{results}"
                    )
                    assert len(r) == len(set(r))
                # duration = 1 / (432 // 8 * 2 ** (n - 2) - hz)
                # duration = 100 * math.pi * duration
                # self.beeps.play(frequency=hz)
                # sleep(result_list[0][1])
                # self.beeps.stop(0)
                # for i in range(1, len(result_list)):
                #     print(
                #      f"time={time} | data={data} | " +
                #      f"hz={result_list[i][0]} | duration={result_list[i][1]}"
                #     )
                #     sleep(result_list[i][1] - result_list[i-1][1])
                #     self.beeps.stop(0)
        raw_file.close()

        # plt.plot(fx)
        # plt.show()


class clockdemoapp(App):
    def build(self):
        w = ClockWidget()
        w.cols = 1
        return w


if __name__ == "__main__":
    pre_init(44100, -16, 1, 1024)
    pygame.init()
    clockdemoapp().run()
