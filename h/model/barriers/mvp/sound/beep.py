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

from model.barriers.mvp.sound.cpu8 import CPU8

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
        n = 4
        limits = [1 * 2 ** i for i in range(n-3)]
        cpus = []
        for limit in limits:
            cpus.append(CPU8(limit=limit, n=10))
        # raw_file = open("input.raw.txt", mode="rb")
        # rnd = random.SystemRandom(0)
        r = []
        for time in range(1, 10):
            # data = raw_file.read(1)
            for data in range(256):
                # data = int.from_bytes(data, byteorder="big")
                result = {}
                for cpu in cpus:
                    uniq = ""
                    results = cpu.get(raw=data, seek=time)
                    # result[sum(results.keys()) // len(results)] = \
                    #        sum(results.values()) // len(results)
                    # r.append(results)
                    print(
                        f"time={time} | data={data} | " +
                        f"{results}"
                    )
                    for i in range(len(results)):
                        for key, value in results[i].items():
                            values = []
                            for val in value:
                                values.append(val)
                            uniq += str(i) + str(key).rjust(3, '0') + \
                                    "".join(map(str, values))
                    r.append(uniq)
                # result_list = sorted(result.items(), key=lambda x: x[1])
                # result_dict = dict(result_list)
                # for hz, _ in results.items():
                #     duration = 1 / (432 // 8 * 2 ** (n - 2) - hz)
                #     duration = 100 * math.pi * duration
                    # result_dict[hz] = duration
                    # self.beeps.play(frequency=hz)
                # result_list = sorted(result_dict.items(), key=lambda x: x[1])

                # sleep(result_list[0][1])
                # self.beeps.stop(0)
                # for i in range(1, len(result_list)):
                #     print(
                #         f"time={time} | data={data} | " +
                #         f"hz={result_list[i][0]} | duration={result_list[i][1]}"
                #     )
                #     sleep(result_list[i][1] - result_list[i-1][1])
                #     self.beeps.stop(0)
            assert len(r) == len(set(r))
        # raw_file.close()

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
