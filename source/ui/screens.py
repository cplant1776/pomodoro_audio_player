from kivy.uix.screenmanager import Screen, ScreenManager
from kivy.uix.popup import Popup
from source.functions import extract_file_paths, get_playlist_song_titles
from kivy.properties import NumericProperty, StringProperty, ObjectProperty
from kivy.clock import Clock
from time import sleep
import datetime
from functools import partial

# ====================================
# CONSTANTS
# ====================================
TIME_MULTIPLIER = {'SECONDS': 1, 'MINUTES': 60, 'HOURS': 3600}

# ====================================
# PARAMETERS
# ====================================
TIME_UNIT = 'MINUTES'


class RootScreen(ScreenManager):
    def __init__(self, session, **kwargs):
        super().__init__(**kwargs)
        self.session = session


class StartScreen(Screen):
    # Fires on move to next screen - default intervals: 25/5/15 minutesS
    def update_intervals(self, work_interval, rest_interval, long_rest_interval, num_of_intervals):
        # Update intervals with duration
        self.parent.session.interval_duration['work'] = int(work_interval) * TIME_MULTIPLIER[TIME_UNIT]
        self.parent.session.interval_duration['rest'] = int(rest_interval) * TIME_MULTIPLIER[TIME_UNIT]
        self.parent.session.interval_duration['long_rest'] = int(long_rest_interval) * TIME_MULTIPLIER[TIME_UNIT]
        self.parent.session.set_intervals_per_session(num_of_intervals)


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
        # Generate list of format [song1, song1 directory, song2, song2 directory,... songN, songN directory]
        new_playlist_file_paths = extract_file_paths(path, filename)
        # Get current_playlist type (work/rest/long_rest)
        playlist_type = str(self.parent.session.current_type).lower()

        if playlist_type == 'work':
            # Generate playlist
            self.parent.session.generate_local_playlist_object(file_paths=new_playlist_file_paths,
                                                               playlist_type='work')
            # Update label text on screen to show songs in playlist
            self.ids['lf_work'].ids['scrollable_label'].text = get_playlist_song_titles(file_paths=new_playlist_file_paths)
        elif playlist_type == 'rest':
            self.parent.session.generate_local_playlist_object(file_paths=new_playlist_file_paths,
                                                               playlist_type='rest')
            self.ids['lf_rest'].ids['scrollable_label'].text = get_playlist_song_titles(file_paths=new_playlist_file_paths)
        elif playlist_type == 'long rest':
            self.parent.session.generate_local_playlist_object(file_paths=new_playlist_file_paths,
                                                               playlist_type='long_rest')
            self.ids['lf_long_rest'].ids['scrollable_label'].text = get_playlist_song_titles(file_paths=new_playlist_file_paths)

        # Close the window
        self.dismiss_popup()

    def update_playlist_label(self):
        pass


class SourceScreen(Screen):
    pass


class LoginScreen(Screen):
    session_style = StringProperty("")

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.submission_data = {}

    def open_load_screen(self, submission_type, username, password):
        print("open load screen")
        self.parent.ids['loading_screen'].set_parameters(submission_type, username, password)
        self.parent.current = 'LoadingScreen'


class LoadingScreen(Screen):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.submission_type = None
        self.username = None
        self.password = None

    def on_enter(self, *args):
        self.submit_form()

    def set_parameters(self, submission_type, username, password):
        self.submission_type = submission_type
        self.username = username
        self.password = password

    def submit_form(self):
        print("Scheduled submit_form")
        print("Submission type: {}".format(self.submission_type))
        if self.submission_type == 'BrainFM':
            self.parent.session.generate_brain_fm_playlist(username=self.username, password=self.password)
            self.parent.session.initialize_session_intervals()
            self.parent.current = 'SessionScreen'


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
        self.ids.interval_time_remaining.text = str(
            datetime.timedelta(seconds=self.parent.session.Timer.get_event_time_remaining()))


    def pause_session_progress(self):
        # Stop counting
        self.progress_value_event.cancel()

    def schedule_skip_interval_progress(self):
        Clock.schedule_once(self.skip_interval_progress, 0.5)

    def skip_interval_progress(self, *args):
        # Update progress bar for skipped interval
        self.progress_value = self.parent.session.Timer.time_passed_since_start


class TesterScreen(LocalFilesScreen):
    pass

