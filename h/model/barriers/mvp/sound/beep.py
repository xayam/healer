import random
import sys
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
        n = 1 + 8 + 1
        limits = [432 // 8 * 2 ** i for i in range(n-2)]
        cpus = []
        for limit in limits:
            cpus.append(CPU8(limit=limit, n=n))
        raw_file = open("input.raw.txt", mode="rb")
        rnd = random.SystemRandom(0)
        data = 1
        time = 0
        while data:
            data = raw_file.read(1)
            if data:
                data = int.from_bytes(data, byteorder="big")
                frequency = []
                durations = []
                for cpu in cpus:
                    cpu.clear()
                    _, _ = cpu.get(raw=0, seek=time)
                    results = cpu.get(raw=data, seek=1)
                    for r in results:
                        print(
                            f"time={time} | data={data} | " +
                            f"hz={r['hz']} | duration={r['duration']}"
                        )
                        self.beeps.play(frequency=r['hz'])
                    sleep(results[0]['duration'])
                    for i in range(len(results[1:])):
                        sleep(results[i]['duration'] - results[i-1]['duration'])
                        self.beeps.stop(0)
            time += 1
        raw_file.close()

class clockdemoapp(App):
    def build(self):
        w = ClockWidget()
        w.cols = 1
        return w


if __name__ == "__main__":
    pre_init(44100, -16, 1, 1024)
    pygame.init()
    clockdemoapp().run()
