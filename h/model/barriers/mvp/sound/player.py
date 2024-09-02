import threading

import pygame
from pygame.mixer import pre_init

from kivy.app import App
from kivy.uix.gridlayout import GridLayout
from kivy.core.window import Window

from model.barriers.mvp.sound.beep import Beeps
from model.barriers.mvp.sound.process import Process

Window.size = (720, 400)

class ClockWidget(GridLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.process = None
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
        self.process = Process(self.beeps)
        thread = threading.Thread(target=self.process.main, args=[])
        thread.start()
        # self.val = int(self.ids.t1.text)
        self.ev = []
        self.ids.b1.disabled = True
        

class Player(App):
    def build(self):
        w = ClockWidget()
        w.cols = 1
        return w
        
        
if __name__ == "__main__":
    pre_init(44100, -16, 1, 1024)
    pygame.init()
    Player().run()
    