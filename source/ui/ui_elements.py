# Standard Library Imports
from math import isclose

# Third Party Imports
from kivy.app import App
from kivy.clock import Clock
from kivy.properties import StringProperty, NumericProperty
from kivy.uix.behaviors import ButtonBehavior
from kivy.uix.image import Image
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.bubble import Bubble
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.modalview import ModalView
from kivy.uix.scrollview import ScrollView
from kivy.uix.textinput import TextInput
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
    def on_release(self):
        self.parent.parent.parent.parent.suspend_buttons()


class FailedSubmissionPopup(ModalView):
    def __init__(self, message, **kwargs):
        super(ModalView, self).__init__(**kwargs)
        self.ids.failed_submission_label.text = message + "\nAre you sure you wish to continue?"


class UniversalHelpPopup(ModalView):
    def __init__(self, display_text, **kwargs):
        super(ModalView, self).__init__(**kwargs)
        self.ids.help_label.text = display_text
        # Hide black background
        self.background_color = (0, 0, 0, 0)
        # Make invisible
        self.opacity = 0

    def fade_in_help_pop(self):
        self.fade_tick_event = Clock.schedule_interval(self.fade_tick, 1 / 50)

    def fade_tick(self, *args):
        if isclose(self.opacity, 1, abs_tol=10**-2):
            self.fade_tick_event.cancel()
        else:
            self.opacity += 1/15


class StartScreenRow(BoxLayout):
    out_value = NumericProperty(0)
    initial_value = NumericProperty(0)
    display_text = StringProperty('')
    slider_max = NumericProperty(60)


class StartScreenTextInput(TextInput):
    def __init__(self, **kwargs):
        super(StartScreenTextInput, self).__init__(**kwargs)

    def validate_text(self, root):
        if int(self.text) < root.slider_max + 1:
            self.text = self.text and self.text[:2]
            # StartScreen function
            root.parent.parent.hide_textinput_error_label()
        else:
            self.text = str(root.initial_value)
            # StartScreen function
            root.parent.parent.show_textinput_error_label()
        root.out_value = int(self.text)


class SelectedSpotifyPlaylistBox(BoxLayout):
    display_title = StringProperty('display title')
    selected_playlist_name = StringProperty('playlist name')
    selected_playlist_img_url = StringProperty('./assets/images/placeholder.jpg')

    def __init__(self, **kwargs):
        super(SelectedSpotifyPlaylistBox, self).__init__(**kwargs)