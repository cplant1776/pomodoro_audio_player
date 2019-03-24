# Standard Library Imports
import datetime
import os
from threading import Thread

# Third Party Imports
from kivy.app import App
from kivy.clock import Clock
from kivy.properties import NumericProperty, StringProperty, ObjectProperty
from kivy.uix.screenmanager import Screen, ScreenManager
from kivy.uix.popup import Popup
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials

# Local Imports
from source.functions import extract_file_paths, get_playlist_song_titles
from source.session.session import Session
from source.ui.ui_elements import FailedSubmissionPopup, UniversalHelpPopup, SearchResultsThumbnail

# ====================================
# CONSTANTS
# ====================================
TIME_MULTIPLIER = {'SECONDS': 1, 'MINUTES': 60, 'HOURS': 3600}
PUBLIC_SPOTIFY_CLIENT_ID = 'fda8d241ac5f41d18df47391d853accb'
PUBLIC_SPOTIFY_CLIENT_SECRET = '3c30c5317e5a4b9398f599a26e9ac428'

# ====================================
# PARAMETERS
# ====================================
TIME_UNIT = 'MINUTES'


class RootScreen(ScreenManager):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.session = Session(self)

    @staticmethod
    def end_app():
        quit()


class StartScreen(Screen):
    # Transition to source selection screen
    def change_screen(self):
        self.update_intervals()
        self.parent.transition.direction = 'left'
        self.parent.current = 'SourceScreen'

    # Set interval duration and number per session
    def update_intervals(self):
        work_interval, rest_interval, long_rest_interval, num_of_intervals = self.values
        # Update intervals with duration
        self.parent.session.interval_duration['work'] = work_interval * TIME_MULTIPLIER[TIME_UNIT]
        self.parent.session.interval_duration['rest'] = rest_interval * TIME_MULTIPLIER[TIME_UNIT]
        self.parent.session.interval_duration['long_rest'] = long_rest_interval * TIME_MULTIPLIER[TIME_UNIT]
        self.parent.session.set_intervals_per_session(num_of_intervals)

    #
    def check_values_validity(self, work_interval, rest_interval, long_rest_interval, num_of_intervals):
        # Store values as ints
        self.values = [work_interval, rest_interval, long_rest_interval, num_of_intervals]
        self.values = [int(n) for n in self.values]
        # Get warnings about the user's settings
        warning_message = self.find_warnings()
        if warning_message:
            # Open a warning popup
            self.pop_warning(warning_message)
        else:
            self.change_screen()

    def pop_warning(self, message):
        self.popup = FailedSubmissionPopup(message=message)
        self.popup.open()

    def find_warnings(self):
        """
        Check the validity of values the user is setting

        w_i: work interval
        r_i: rest interval
        lr_i: long-rest interval
        n_o_i: number of work intervals per session
        """
        w_i, r_i, lr_i, n_o_i = self.values
        if w_i < r_i:
            return "Work interval is shorter than rest interval. "
        elif r_i > lr_i:
            return "Rest interval is longer than long rest interval. "
        elif r_i > w_i * 0.5:
            return "Rest interval is too long for your chosen work interval. "
        elif n_o_i < 4:
            return "The number of work intervals per session is too low. "
        return False

    def pop_help(self):
        help_text = """
        'Lorem ipsum dolor sit amet, consectetur adipiscing elit. Suspendisse consectetur eget nunc eget maximus. Nam condimentum porta lacinia. Pellentesque ultrices nisi quis volutpat iaculis. Quisque dictum sem nec dignissim auctor. In hac habitasse platea dictumst. Pellentesque habitant morbi tristique senectus et netus et malesuada fames ac turpis egestas. Fusce velit augue, eleifend a accumsan ut, pretium non augue. Praesent id imperdiet lectus, vel suscipit elit. Pellentesque ut neque ante. Mauris a turpis ullamcorper arcu facilisis cursus in pretium purus. Proin luctus a arcu eu cursus. Aenean congue ultrices commodo.
        
    Vestibulum sed nulla commodo, posuere velit id, semper turpis. Donec facilisis interdum ex, eget lacinia magna. Quisque eros mauris, hendrerit elementum condimentum pellentesque, condimentum rhoncus elit. Fusce finibus rutrum posuere. Aenean augue ante, bibendum sed quam eget, consectetur hendrerit enim. Nulla condimentum sagittis tortor sed volutpat. Integer dapibus iaculis neque, ut volutpat mi venenatis id. Aenean ut ex diam. Integer fringilla condimentum enim, eu suscipit velit egestas a. Nulla a rhoncus diam.'
        """
        self.popup = UniversalHelpPopup(help_text)
        self.popup.open()
        self.popup.fade_in_help_pop()

    def show_textinput_error_label(self):
        self.ids.error_label.color = (1, 0, 0, 1)

    def hide_textinput_error_label(self):
        self.ids.error_label.color = (1, 0, 0, 0)


class LocalFilesScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.saved_directory = os.path.abspath(os.sep)

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

        self.saved_directory = path

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
    def pop_help(self):
        help_text = """
        Different Lorem ipsum dolor sit amet, consectetur adipiscing elit. Phasellus dapibus faucibus ultrices. Nam convallis neque sed enim dignissim commodo. Vivamus nisi erat, euismod viverra nunc id, efficitur sollicitudin massa. Cras sagittis nibh eget sapien lacinia malesuada. Vivamus at nisi et leo efficitur ornare vitae et lorem. Praesent dapibus maximus sapien vel accumsan. Vivamus pretium tellus a vulputate finibus.

Curabitur non tortor pretium, sodales ipsum non, feugiat leo. Sed velit risus, varius sed enim at, fermentum rhoncus augue. In vestibulum elit id cursus posuere. In mattis elementum neque, quis feugiat erat pretium in. Cras quis urna quis massa iaculis viverra. Fusce posuere, lacus eu fermentum placerat, sapien nisi gravida ipsum, nec ullamcorper enim ex a lorem. Proin gravida elementum dolor, sodales porta mi suscipit nec. Fusce velit tortor, semper vel egestas quis, lobortis a dui. 
        """
        self.popup = UniversalHelpPopup(help_text)
        self.popup.open()
        self.popup.fade_in_help_pop()


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
        # Use thread so that loading animation can continue while loading
        brain_fm_thread = Thread(target=self.submit_form)
        brain_fm_thread.start()

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
            # Close thread
            return


class BrowseFilesScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    @staticmethod
    def cancel():
        app = App.get_running_app()
        app.root.ids['local_files_screen'].dismiss_popup()


class SessionScreen(Screen):
    progress_max = NumericProperty(0)
    progress_value = NumericProperty(100)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
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
        try:
            self.progress_value = self.parent.session.Timer.time_passed_since_start
        except AttributeError:
            print("Error A")

    def suspend_buttons(self):
        buttons = self.ids.button_box.children
        for button in buttons:
            button.disabled = True
        Clock.schedule_once(self.resume_buttons, 0.3)

    def resume_buttons(self, *args):
        buttons = self.ids.button_box.children
        for button in buttons:
            button.disabled = False

    def end_current_session(self):
        self.reset_values()
        self.pause_session_progress()
        self.parent.current = 'SessionOverScreen'

    def reset_values(self):
        self.progress_max = 0
        self.progress_value = 100


class SessionOverScreen(Screen):
    pass


class SpotifyPlaylistsScreen(Screen):
    pass


class TesterScreen(Screen):
    pass


class SpotifySearchScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def send_search_query(self, search_string):
        # Connect to spotify API
        client_credentials_manager = SpotifyClientCredentials(client_id=PUBLIC_SPOTIFY_CLIENT_ID,
                                                              client_secret=PUBLIC_SPOTIFY_CLIENT_SECRET)
        sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager)
        # Run playlist search with search_string
        results = sp.search(q=search_string, limit=20, type='playlist')
        # Create thumbnails from the results
        self.ids.results_scrollview.populate_thumbnails(results)

    @staticmethod
    def cancel():
        app = App.get_running_app()
        app.root.ids['spotify_search_screen'].dismiss_popup()

