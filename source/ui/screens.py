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
from source.session.playlists.brain_fm_playlist import BrainFMBrowser, BrainFMPlaylist
from source.session.session import Session
from source.ui.ui_elements import FailedSubmissionPopup, UniversalErrorPopup, UniversalHelpPopup, SearchResultsThumbnail

# ====================================
# CONSTANTS
# ====================================
TIME_MULTIPLIER = {'SECONDS': 1, 'MINUTES': 60, 'HOURS': 3600}
PUBLIC_SPOTIFY_CLIENT_ID = 'fda8d241ac5f41d18df47391d853accb'
PUBLIC_SPOTIFY_CLIENT_SECRET = '3c30c5317e5a4b9398f599a26e9ac428'
PLAYLIST_EXTENSIONS = ['m3u', 'm3u8', 'pls']

# ====================================
# PARAMETERS
# ====================================
TIME_UNIT = 'MINUTES'


class RootScreen(ScreenManager):
    previous_screen = StringProperty("SourceScreen")

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

    def show_error(self, error_text):
        self._popup = UniversalErrorPopup(error_text)
        self._popup.open()

    def load(self, path, filename):
        # Check for valid file extension
        playlist_file = filename[0]
        if not playlist_file.endswith(tuple(PLAYLIST_EXTENSIONS)):
            self.dismiss_popup()
            self.show_error(error_text="Unsupported filetype selected. Please select a M3U, M3U8, or PLS file.")
            return
        else:
            # Generate list of format [song1, song1 directory, song2, song2 directory,... songN, songN directory]
            new_playlist_file_paths = extract_file_paths(path, filename)
            # Get current_playlist type (work/rest/long_rest)
            playlist_type = str(self.parent.session.current_type).lower()

            self.saved_directory = path

            self.generate_local_playlist(playlist_type=playlist_type, file_paths=new_playlist_file_paths)
            self.update_display_text(playlist_type=playlist_type, file_paths=new_playlist_file_paths)

            # Close the window
            self.dismiss_popup()

    def generate_local_playlist(self, file_paths, playlist_type):
        self.parent.session.generate_local_playlist_object(file_paths=file_paths, playlist_type=playlist_type)

    def update_display_text(self, playlist_type, file_paths):
        if playlist_type == 'work':
            self.ids['lf_work'].ids['scrollable_label'].text = get_playlist_song_titles(file_paths=file_paths)
        elif playlist_type == 'rest':
            self.ids['lf_rest'].ids['scrollable_label'].text = get_playlist_song_titles(file_paths=file_paths)
        elif playlist_type == 'long rest':
            self.ids['lf_long_rest'].ids['scrollable_label'].text = get_playlist_song_titles(file_paths=file_paths)


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

    def on_enter(self, *args):
        self.parent.transition.direction = 'left'

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

    def on_pre_enter(self, *args):
        # Use thread so that loading animation can continue while loading
        print("entered LoginScreen")
        submission_thread = Thread(target=self.submit_form)
        submission_thread.start()
        self.ids['connecting_animation'].start_animation()

    def on_leave(self, *args):
        print("exit LoginScreen")
        self.ids['connecting_animation'].stop_animation()

    def set_parameters(self, submission_type, username, password):
        self.submission_type = submission_type
        self.username = username
        self.password = password

    def submit_form(self):
        print("Scheduled submit_form")
        print("Submission type: {}".format(self.submission_type))

        # Change login credentials if driver already exists, else create driver
        if self.parent.session.driver:
            print("1")
            self.parent.session.driver.update_credentials(username=self.username, password=self.password)
        else:
            self.parent.session.create_driver(self.submission_type, self.username, self.password)

        # Check for valid credentials. If not found, return to LoginScreen
        if self.parent.session.has_valid_credentials():

            if self.submission_type == 'BrainFM':
                self.parent.session.generate_brain_fm_playlist()
            elif self.submission_type == 'Spotify':
                self.parent.session.generate_spotify_playlist()

            self.parent.session.initialize_session_intervals()
            self.parent.current = 'SessionScreen'

        else:
            print("Invalid credentials given")
            self.parent.transition.direction = 'right'
            self.parent.current = 'LoginScreen'

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

    playback_image = StringProperty('./assets/images/coming_soon.png')
    playback_artist = StringProperty('Initial Artist')
    playback_album = StringProperty('Initial Album')
    playback_title = StringProperty('Initial Title')

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.progress_value_event = None
        self.app = App.get_running_app()

    def start_session_progress(self):
        session = self.parent.session
        if session.Intervals[session.interval_loop].playback_active:
            print("state_session_progress: playback already active")
        else:
            # Set max progress to total time of session
            self.progress_max = self.parent.session.get_session_total_time()
            # Increment progress value every 1 sec
            self.progress_value_event = Clock.schedule_interval(self.update_session_progress, 1)
            print("PROGRESS MAX: {}".format(self.progress_max))

    def update_session_progress(self, *args):
        self.progress_value += 1
        try:
            self.ids.interval_time_remaining.text = str(
                datetime.timedelta(seconds=self.parent.session.Timer.get_event_time_remaining()))
        except AttributeError:
            pass

    def pause_session_progress(self):
        session = self.parent.session
        if session.Intervals[session.interval_loop].playback_active:
            # Stop counting
            self.progress_value_event.cancel()
        else:
            print("pause_session_progress: no playback active")

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

    def dismiss_popup(self):
        self._popup.dismiss()

    def pop_file_browser(self):
        content = BrowseFilesScreen(load=self.load)
        # Popup a file browser to select current_playlist
        self._popup = Popup(title="Load file", content=content,
                            size_hint=(0.75, 0.75))
        self._popup.open()

    def show_error(self, error_text):
        self._popup = UniversalErrorPopup(error_text)
        self._popup.open()

    def load(self, path, filename):
        if "spotify" in filename:
            session = self.parent.session
            session.Intervals[session.interval_loop].playlist.set_device_id()
        else:
            self.dismiss_popup()
            self.show_error(error_text="Not a valid location. Now ending session. Please wait a moment . . .")
            Clock.schedule_once(self.return_to_start_screen(), 5)

    def return_to_start_screen(self):
        session = self.parent.session
        session.end_interval()
        session.end_session()
        app = App.get_running_app()
        app.root.current = 'StartScreen'


class SessionOverScreen(Screen):
    pass


class SpotifyPlaylistsScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def dismiss_popup(self):
        self._popup.dismiss()

    def show_load(self, playlist_type):
        content = SpotifySearchScreen(playlist_type=playlist_type, load=self.load)
        # Popup a file browser to select current_playlist
        self._popup = Popup(title="Select a Playlist", content=content)
        self._popup.open()

    def load(self, playlist_type, playlist_info):
        box_id_selector = {'work': 'work_playlist_name',
                           'rest': 'rest_playlist_name',
                           'long rest': 'long_rest_playlist_name'}
        box_id = box_id_selector[playlist_type.lower()]
        self.update_box_info(self.ids[box_id], playlist_info)

        # Close the window
        self.dismiss_popup()

    def update_box_info(self, box, playlist_info):
        box.selected_playlist_img_path = playlist_info['img_path']
        box.selected_playlist_name = playlist_info['playlist_name']
        box.selected_playlist_uri = playlist_info['playlist_uri']
        box.draw_playlist_label_background()

    def submit_playlists(self):
        # if self.all_playlists_selected():
        app = App.get_running_app()
        root_screen = app.root
        root_screen.transition_direction = 'left'
        root_screen.previous_screen = 'SpotifyPlaylistsScreen'
        root_screen.current = 'LoginScreen'
        # else:
        #     # TODO: Add error popup
        #     print("Not all playlists selected!")
        pass

    def all_playlists_selected(self):
        for thumbnail_box in self.ids.playlist_select_container.children:
            if thumbnail_box.selected_playlist_uri == '':
                return False
        return True


class TesterScreen(Screen):
    pass


class SpotifySearchScreen(Screen):
    playlist_type = StringProperty('')

    def __init__(self, playlist_type=None, load=None, **kwargs):
        super().__init__(**kwargs)
        if playlist_type:
            self.playlist_type = playlist_type
        if load:
            self.load = load

    def send_search_query(self, search_string):
        # Connect to spotify API
        client_credentials_manager = SpotifyClientCredentials(client_id=PUBLIC_SPOTIFY_CLIENT_ID,
                                                              client_secret=PUBLIC_SPOTIFY_CLIENT_SECRET)
        sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager)
        # Run playlist search with search_string
        results = sp.search(q=search_string, limit=10, type='playlist')
        # Create thumbnails from the results
        self.ids.results_scrollview.populate_thumbnails(results)

    def submit_selection(self):
        # Find selected thumbnail
        for thumbnail in self.ids.results_scrollview.ids.content_box.children:
            if hasattr(thumbnail, 'rect'):
                # Capture thumbnail data
                data = {'img_path': thumbnail.img_path,
                        'playlist_name': thumbnail.playlist_name,
                        'playlist_uri': thumbnail.playlist_uri}
                app = App.get_running_app()
                app.root.ids['spotify_playlist_screen'].load(self.playlist_type, data)
                break


    @staticmethod
    def cancel():
        app = App.get_running_app()
        app.root.ids['spotify_search_screen'].dismiss_popup()

