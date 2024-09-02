import numpy

import pygame
from pygame.mixer import Sound


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
