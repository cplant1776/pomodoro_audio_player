# Standard Library Imports

# Third Party Imports
from kivy.clock import Clock
from kivy.properties import StringProperty, NumericProperty
from kivy.uix.behaviors import ButtonBehavior
from kivy.uix.image import Image
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.scrollview import ScrollView
from kivy.uix.progressbar import ProgressBar

# Local Imports


class ScrollableLabel(ScrollView):
    text = StringProperty('')


class SessionScreenProgressBar(ProgressBar):
    progress_max = NumericProperty(None)
    progress_value = NumericProperty(None)


class ConnectingLabel(Label):
    angle = NumericProperty(0)
    startCount = NumericProperty(20)
    count = NumericProperty(0)

    def __init__(self, **kwargs):
        super(ConnectingLabel, self).__init__(**kwargs)
        Clock.schedule_once(self.set_Circle, 0.1)
        self.count = self.startCount
        # self.angle = 0

    def set_Circle(self, dt):
        self.angle = self.angle + dt*360
        if self.angle >= 360:
            self.angle = 0
            self.count = self.count - 1
        if self.count > 0:
            Clock.schedule_once(self.set_Circle, 1.0/360)


class SessionScreenButton(Button):
    # background_normal = "normal.png"
    # background_down = "pressed.png"
    # background_disabled_normal = "normal.png"

    def on_release(self):
        self.parent.parent.parent.parent.suspend_buttons()
