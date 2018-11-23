from kivy.uix.screenmanager import Screen, ScreenManager
from kivy.uix.popup import Popup
from source.functions import parse_playlist_file
from kivy.properties import NumericProperty
from kivy.clock import Clock

import os.path


class RootScreen(ScreenManager):
    def __init__(self, session, **kwargs):
        super().__init__(**kwargs)
        self.session = session


class StartScreen(Screen):
    # Fires on move to next screen - default intervals: 25/5/15
    def update_intervals(self, work_interval, rest_interval, long_rest_interval):
        # Update intervals with duration in SECONDS (multiply by 60)
        self.parent.session.work_interval = work_interval * 60
        self.parent.session.rest_interval = rest_interval * 60
        self.parent.session.long_rest_interval = long_rest_interval * 60


class LocalFilesScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def dismiss_popup(self):
        self._popup.dismiss()

    def show_load(self):
        content = BrowseFilesScreen(load=self.load)
        # Popup a file browser to select current_playlist
        self._popup = Popup(title="Load file", content=content,
                            size_hint=(0.75, 0.75))
        self._popup.open()

    def load(self, path, filename):
        # Generate list of format [(song1), (song1 directory), (song2), (song2 directory),...]
        new_playlist = parse_playlist_file(path, filename)
        # Get current_playlist type (work/rest/long_rest)
        playlist_type = str(self.parent.session.current_type).lower()

        # Update appropriate current_playlist then update label text to display songs in the current_playlist
        if playlist_type == 'work':
            self.parent.session.work_playlist = new_playlist
            self.ids['lf_work'].ids['scrollable_label'].text = self.parent.session.get_songs_string(new_playlist)
        elif playlist_type == 'rest':
            self.parent.session.rest_playlist = new_playlist
            self.ids['lf_rest'].ids['scrollable_label'].text = self.parent.session.get_songs_string(new_playlist)
        elif playlist_type == 'long rest':
            self.parent.session.long_rest_playlist = new_playlist
            self.ids['lf_long_rest'].ids['scrollable_label'].text = self.parent.session.get_songs_string(new_playlist)

        # Close the window
        self.dismiss_popup()

    def update_playlist_label(self):
        pass


class SourceScreen(Screen):
    pass


class BrowseFilesScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def cancel(self):
        self.parent.root.dismiss_popup()


class SessionScreen(Screen):
    progress_max = NumericProperty(None)
    progress_value = NumericProperty(None)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.tester_text = 2

        self.progress_value = 0
        self.progress_max = 100

    def start_interval_progress(self):
        self.progress_max = int(self.parent.session.Timer.time_passed_since_start - self.parent.session.Timer.total_time)
        self.progress_value_event = Clock.schedule_interval(self.update_interval_progress, 1)
        print(self.progress_max)

    def update_interval_progress(self, *args):
        self.progress_value += 1
        # print(self.progress_value)

    def pause_interval_progress(self):
        # Stop counting
        self.progress_value_event.cancel()

    def skip_interval_progress(self):
        # Update progress bar for skipped interval
        self.progress_value = self.parent.session.Timer.time_passed_since_start


class TesterScreen(Screen):
    pass

