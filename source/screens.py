from kivy.uix.screenmanager import Screen, ScreenManager
from kivy.uix.popup import Popup
from source.functions import parse_playlist_file
from kivy.properties import StringProperty

import os.path


class RootScreen(ScreenManager):
    def __init__(self, session, **kwargs):
        super().__init__(**kwargs)
        self.session = session


class StartScreen(Screen):
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
        self._popup = Popup(title="Load file", content=content,
                            size_hint=(1, 1))
        self._popup.open()

    def load(self, path, filename):
        # Get list of format [(song1), (song1 directory), (song2), (song2 directory),...]
        new_playlist = parse_playlist_file(path, filename)
        # Get playlist type for conditional statements
        playlist_type = str(self.parent.session.current_type).lower()

        # Update appropriate playlist then update label text to display songs in the playlist
        if playlist_type == 'work':
            self.parent.session.work_playlist = new_playlist
            self.ids['lf_work'].ids['scrollable_label'].text = self.parent.session.get_songs_string(new_playlist)
        elif playlist_type == 'rest':
            self.parent.session.rest_playlist = new_playlist
            self.ids['lf_rest'].ids['scrollable_label'].text = self.parent.session.get_songs_string(new_playlist)
        elif playlist_type == 'long rest':
            self.parent.session.long_rest_playlist = new_playlist
            self.ids['lf_long_rest'].ids['scrollable_label'].text = self.parent.session.get_songs_string(new_playlist)


        self.dismiss_popup()

    def update_playlist_label(self):
        pass


class SourceScreen(Screen):
    pass


class BrowseFilesScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)


class SessionScreen(Screen):
    pass

class TesterScreen(Screen):
    pass

