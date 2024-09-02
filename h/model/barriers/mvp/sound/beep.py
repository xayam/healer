import threading
import numpy
import pygame
from pygame.mixer import Sound, pre_init
from kivy.app import App
from kivy.uix.gridlayout import GridLayout
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
        scheme = {
            # "x": 16, "y": 16, "z": 16,
            # "r": 8,
            # "g": 4,
            # "b": 4,
            "c": 4,
        }
        scheme_protect = {}
        for s in scheme:
            scheme_protect[s] = 1 + scheme[s] + 1
        dimension = sum(scheme.values())
        cpu = {}
        r = {}
        for index in scheme:
            cpu[index] = CPU(n=scheme_protect[index])
        raw_file = open("input.raw.txt", mode="rb")
        ending = ""
        for seek in range(1, 12):
            dataset = []
            for index in scheme:
                r[index] = []
            dim = dimension - len(ending)
            count_bytes = \
                dim // 8 if dim % 8 == 0 \
                else dim // 8 + 1
            data = raw_file.read(count_bytes)
            data = int.from_bytes(data, byteorder="big")
            data = f"{data:{8 * count_bytes}b}".replace(' ', '0')
            data = ending + data
            start = 0
            for index in scheme:
                raw = data[start:start + scheme[index]]
                raw = raw.rjust(scheme[index], '0')
                dataset.append({index: raw})
                start += scheme[index]
            ending = data[start:]

            dataset = []
            for index in scheme:
                for data in range(2 ** scheme[index]):
                    raw = f"{data:{scheme[index]}b}". \
                        replace(' ', '0')
                    dataset.append({index: raw})

            for chunk in dataset:
                for index, raw in chunk.items():
                    uniq = ""
                    summa = 0
                    results = cpu[index].get(raw=raw, seek=seek)
                    for i in range(len(results)):
                        for key, value in results[i].items():
                            buffer = []
                            for v in value:
                                buffer.append(key + v)
                            uniq += "|" + str(key).rjust(2, '0') + \
                                    "|" + "|".join(
                                map(lambda x: str(x).rjust(
                                    2, '0'),
                                    value))
                            summa += sum(buffer)
                    r[index].append(uniq)
                    print(
                        f"seek={str(seek).rjust(2, ' ')} | " +
                        f"raw={str(raw).rjust(max(scheme.values()), ' ')} | " +
                        f"summa={str(summa).rjust(4, ' ')} " +
                        f"{r[index][-1]}"
                    )
                    assert len(r[index]) == len(set(r[index]))
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
