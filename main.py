from kivy.app import App
from kivy.lang import Builder
import os.path
import source.screens as screens
import source.ui_elements as ui_elements
from time import sleep
from source.session import Session

KV_FILE = 'pomodoro.kv'


# Change directories because kv
# had trouble including from a relative path
def load_kv_file(kv):
    os.chdir("UI")
    Builder.load_file(kv)
    os.chdir("..")


class PomodoroApp(App):
    def build(self):
        load_kv_file(KV_FILE)
        session = Session()
        return screens.RootScreen(session=session)


if __name__ == "__main__":
    PomodoroApp().run()
