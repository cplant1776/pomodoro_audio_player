# Standard Library Imports

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
    # background_normal = "normal.png"
    # background_down = "pressed.png"
    # background_disabled_normal = "normal.png"

    def on_release(self):
        self.parent.parent.parent.parent.suspend_buttons()


class FailedSubmissionPopup(ModalView):
    def __init__(self, message, **kwargs):
        super(ModalView, self).__init__(**kwargs)
        self.ids.failed_submission_label.text = message + "\nAre you sure you wish to continue?"


class HelpPopup(ModalView):
    def __init__(self, **kwargs):
        super(ModalView, self).__init__(**kwargs)
        self.ids.help_label.text = """
Lorem ipsum dolor sit amet, consectetur adipiscing elit. Suspendisse consectetur eget nunc eget maximus. Nam condimentum porta lacinia. Pellentesque ultrices nisi quis volutpat iaculis. Quisque dictum sem nec dignissim auctor. In hac habitasse platea dictumst. Pellentesque habitant morbi tristique senectus et netus et malesuada fames ac turpis egestas. Fusce velit augue, eleifend a accumsan ut, pretium non augue. Praesent id imperdiet lectus, vel suscipit elit. Pellentesque ut neque ante. Mauris a turpis ullamcorper arcu facilisis cursus in pretium purus. Proin luctus a arcu eu cursus. Aenean congue ultrices commodo.

Vestibulum sed nulla commodo, posuere velit id, semper turpis. Donec facilisis interdum ex, eget lacinia magna. Quisque eros mauris, hendrerit elementum condimentum pellentesque, condimentum rhoncus elit. Fusce finibus rutrum posuere. Aenean augue ante, bibendum sed quam eget, consectetur hendrerit enim. Nulla condimentum sagittis tortor sed volutpat. Integer dapibus iaculis neque, ut volutpat mi venenatis id. Aenean ut ex diam. Integer fringilla condimentum enim, eu suscipit velit egestas a. Nulla a rhoncus diam.
        """


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
