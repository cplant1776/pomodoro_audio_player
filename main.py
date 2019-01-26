from kivy.app import App
from kivy.lang import Builder
import os.path
import source.ui.screens as screens
from source.session.session import Session
import source.ui.ui_elements

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

    def on_stop(self):
        """End program if clicking Close"""
        print("I stopped!")
        quit()

    def build(self):
        """Start main loop"""
        session = Session()
        load_kv_file(KV_FILE)
        return screens.RootScreen(session=session)


if __name__ == "__main__":
    PomodoroApp().run()

# TODO: Add protections for user's incorrect use
# TODO: Create load queue to reduce memory usage for local playlists
# TODO: Look into spotify API
