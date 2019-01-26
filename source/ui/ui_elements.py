from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.scrollview import ScrollView
from kivy.properties import StringProperty, NumericProperty
from kivy.uix.progressbar import ProgressBar
from kivy.animation import Animation
from kivy.clock import Clock


class StartScreenLabel(Label):
    pass


class StartScreenTextInput(TextInput):
    pass


class SourceScreenButton(Button):
    pass


class LocalFilesScreenSection(BoxLayout):
    pass


class ScrollableLabel(ScrollView):
    text = StringProperty('')


class SessionScreenProgressBar(ProgressBar):
    progress_max = NumericProperty(None)
    progress_value = NumericProperty(None)


class LoginScreenField(BoxLayout):
    label_text = StringProperty('')


class TestLabel(Label):
    my_text = StringProperty('')


class ConnectingLabel(Label):
    angle = NumericProperty(0)
    startCount = NumericProperty(20)
    count = NumericProperty(0)

    def __init__(self, **kwargs):
        super(ConnectingLabel, self).__init__(**kwargs)
        Clock.schedule_once(self.set_Circle, 0.1)
        self.count = self.startCount
        self.angle = 0

    def set_Circle(self, dt):
        self.angle = self.angle + dt*360
        if self.angle >= 360:
            self.angle = 0
            self.count = self.count - 1
        if self.count > 0:
            Clock.schedule_once(self.set_Circle, 1.0/360)

