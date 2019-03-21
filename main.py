# Standard Library Imports
import os.path
from shutil import rmtree

# Third Party Imports
from kivy.app import App
from kivy.lang import Builder
from kivy.resources import resource_add_path

# Local Imports
from source.session.session import Session
import source.ui.ui_elements
import source.ui.screens as screens


ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
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
        print("Cleaning up . . .")
        # Delete temporary folder and contents
        rmtree('tmp')
        quit()

    def build(self):
        """Start main loop"""
        load_kv_file(KV_FILE)
        return screens.RootScreen()


if __name__ == "__main__":
    # Create temporary directory
    try:
        os.mkdir('tmp')
    except OSError:
        rmtree('tmp')
        os.mkdir('tmp')
    # Launch app
    PomodoroApp().run()
