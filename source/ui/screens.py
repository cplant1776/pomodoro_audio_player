from kivy.uix.screenmanager import Screen, ScreenManager
from kivy.uix.popup import Popup
from source.functions import extract_file_paths
from kivy.properties import NumericProperty, StringProperty
from kivy.clock import Clock
from os import path
from time import sleep


class RootScreen(ScreenManager):
    def __init__(self, session, **kwargs):
        super().__init__(**kwargs)
        self.session = session


class StartScreen(Screen):
    # Fires on move to next screen - default intervals: 25/5/15
    def update_intervals(self, work_interval, rest_interval, long_rest_interval):
        # Update intervals with duration in SECONDS (multiply by 60)
        # self.parent.session.interval_duration['work'] = int(work_interval) * 60
        # self.parent.session.interval_duration['rest'] = int(rest_interval) * 60
        # self.parent.session.interval_duration['long_rest'] = int(long_rest_interval) * 60
        self.parent.session.interval_duration['work'] = int(work_interval)
        self.parent.session.interval_duration['rest'] = int(rest_interval)
        self.parent.session.interval_duration['long_rest'] = int(long_rest_interval)


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
        new_playlist_file_paths = extract_file_paths(path, filename)
        # Get current_playlist type (work/rest/long_rest)
        playlist_type = str(self.parent.session.current_type).lower()

        # Update appropriate type of playlist then update label text to display songs in the current_playlist
        if playlist_type == 'work':
            self.parent.session.generate_local_playlist_object(file_paths=new_playlist_file_paths, playlist_type='work')
            self.ids['lf_work'].ids['scrollable_label'].text = self.get_playlist_song_titles(file_paths=new_playlist_file_paths)
        elif playlist_type == 'rest':
            self.parent.session.generate_local_playlist_object(file_paths=new_playlist_file_paths, playlist_type='rest')
            self.ids['lf_rest'].ids['scrollable_label'].text = self.get_playlist_song_titles(file_paths=new_playlist_file_paths)
        elif playlist_type == 'long rest':
            self.parent.session.generate_local_playlist_object(file_paths=new_playlist_file_paths, playlist_type='long_rest')
            self.ids['lf_long_rest'].ids['scrollable_label'].text = self.get_playlist_song_titles(file_paths=new_playlist_file_paths)

        # Close the window
        self.dismiss_popup()

    def update_playlist_label(self):
        pass

    def get_playlist_song_titles(self, file_paths):
        result = []
        for p in file_paths:
            head, tail = path.split(p)
            result.append(tail)
        result = '\n'.join(result)
        return result


class SourceScreen(Screen):
    pass


class LoginScreen(Screen):
    session_style = StringProperty("")

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def submit_form(self, submission_type='', username='', password=''):
        sleep(1)
        if submission_type == 'BrainFM':
            self.parent.session.generate_brain_fm_playlist(username=username, password=password)
            self.parent.session.initialize_session_intervals()



class LoadingScreen(Screen):
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

        self.progress_value_event = None

    def start_session_progress(self):
        # Set max progress to total time of session
        self.progress_max = self.parent.session.get_session_total_time()
        # Increment progress value every 1 sec
        self.progress_value_event = Clock.schedule_interval(self.update_session_progress, 1)
        print("PROGRESS MAX: {}".format(self.progress_max))

    def update_session_progress(self, *args):
        self.progress_value += 1

    def pause_session_progress(self):
        # Stop counting
        self.progress_value_event.cancel()

    def skip_interval_progress(self):
        # Update progress bar for skipped interval
        self.progress_value = self.parent.session.Timer.time_passed_since_start


class TesterScreen(LocalFilesScreen):
    pass

