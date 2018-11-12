from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.scrollview import ScrollView
from kivy.properties import StringProperty


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

