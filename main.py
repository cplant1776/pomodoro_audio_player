from kivy.app import App
from kivy.lang import Builder
import os.path
import source.ui.screens as screens
from source.session.session import Session

KV_FILE = 'pomodoro.kv'


def load_kv_file(kv):
    # Workaround because kivy had trouble with relative paths
    os.chdir("kv")
    Builder.load_file(kv)
    os.chdir("..")


class PomodoroApp(App):
    def build(self):
        session = Session()
        load_kv_file(KV_FILE)
        return screens.RootScreen(session=session)


if __name__ == "__main__":
    PomodoroApp().run()
