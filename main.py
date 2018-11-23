from kivy.app import App
from kivy.lang import Builder
from kivy.clock import Clock
import os.path
import source.screens as screens
import source.ui_elements as ui_elements
from time import sleep
from source.session import Session

import logging

log = logging.getLogger(__name__)


def do_something():
    log.debug("Doing something!")

KV_FILE = 'pomodoro.kv'


# Change directories because kv
# had trouble including from a relative path
def load_kv_file(kv):
    os.chdir("UI")
    Builder.load_file(kv)
    os.chdir("..")


class PomodoroApp(App):
    def build(self):
        # Clock.max_iterations = 20
        load_kv_file(KV_FILE)
        session = Session()
        return screens.RootScreen(session=session)


if __name__ == "__main__":
    PomodoroApp().run()
