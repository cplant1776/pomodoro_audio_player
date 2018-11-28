from kivy.app import App
from kivy.lang import Builder
import os.path
import source.ui.screens as screens
from source.session.session_local_file import Session

import logging

log = logging.getLogger(__name__)


def do_something():
    log.debug("Doing something!")

KV_FILE = 'pomodoro.kv'


# Change directories because kv
# had trouble including from a relative path
def load_kv_file(kv):
    os.chdir("kv")
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
