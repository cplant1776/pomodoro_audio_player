from kivy.app import App
from kivy.lang import Builder
import os.path
import source.ui.screens as screens
from source.session.session import Session

import tracemalloc
tracemalloc.start()

KV_FILE = 'pomodoro.kv'


def load_kv_file(kv):
    """Loads master kv file in ./kv"""
    # Workaround because kivy had trouble with relative paths
    os.chdir("kv")
    Builder.load_file(kv)
    os.chdir("..")


class PomodoroApp(App):
    def build(self):
        """Start main loop"""
        session = Session()
        load_kv_file(KV_FILE)
        return screens.RootScreen(session=session)


if __name__ == "__main__":
    PomodoroApp().run()

# TODO: Make the interface nicer to look at
# TODO: Create load queue to reduce memory usage
# TODO: Look into spotify API
