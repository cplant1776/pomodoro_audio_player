from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.scrollview import ScrollView
from kivy.properties import StringProperty, NumericProperty
from kivy.uix.progressbar import ProgressBar


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


class TestLabel(Label):
    my_text = StringProperty('')

