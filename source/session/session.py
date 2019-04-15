# Standard Library Imports
from time import strftime

# Third Party Imports
from kivy.clock import Clock
from selenium import webdriver

# Local Imports
from .eventhandler import EventHandler
from .timer import Timer
from source.session.playlists.local_playlist import LocalPlaylist
from source.session.playlists.brain_fm_playlist import BrainFMBrowser, BrainFMPlaylist
from source.session.playlists.spotify_playlist.spotify_playlist import SpotifyPlaybackDevice, SpotifyPlaylist
from source.functions import generate_session_structure
from source.session.interval import Interval


# ===========================
# CONSTANTS
# ===========================


class Session:
    """
    Main class for controlling audio output

    A session holds a list of Intervals. Each Interval represents a work, rest, or long rest period.
    Session will last until all Intervals are completed. Session also controls starting/stopping/skipping Intervals.
    It generates the playlist objects and passes them to each Interval when initializing the Intervals
    """
    def __init__(self, parent):
        # Initialize session empty
        self.interval_duration = {'work': -1, 'rest': -1, 'long_rest': -1}
        self.playlist = {'work': None, 'rest': None, 'long_rest': None}
        self.num_of_work_intervals = None
        self.Intervals = {}
        self.parent = parent
        self.driver = None

        # Initialize timers and eventhandlers
        self.Timer = Timer()
        self.EventHandler = EventHandler()

        # Keep track of which Interval is active
        self.interval_loop = 0

    def start_next_interval(self):
        """Start next interval and schedule event for starting interval after that"""
        print("Start Interval " + str(self.interval_loop))

        # Start interval
        self.Intervals[self.interval_loop].start()
        # Timer event_length = interval_length
        self.Timer.set_event_duration(self.Intervals[self.interval_loop].duration)
        # Time event_time_passed = 0
        self.Timer.reset_event_time_passed()
        # Star session timer
        self.Timer.start()

        # Schedule event to end current interval
        change_interval_event = Clock.schedule_once(self.change_interval,
                                                    self.Timer.event_duration)
        self.EventHandler.schedule_event(event=change_interval_event, event_name='change_interval')

    def change_interval(self, *args):
        """Scheduled event that ends current interval and starts next"""
        print("{} - Execute: {} ==> {}".format(strftime('%X'), "change_interval",
                                               self.EventHandler.events['change_interval']))
        if self.is_final_interval():
            self.end_session()
        else:
            self.end_interval()
            self.interval_loop += 1
            self.start_next_interval()

    def end_interval(self):
        """End current interval"""
        self.Intervals[self.interval_loop].stop()
        # Pause session timer
        self.Timer.pause()

    def skip_interval(self):
        """Skip remainder of current interval and adjust the timer to reflect this"""
        # Unschedule current end event
        self.EventHandler.cancel_event(event_name='change_interval')
        # Unschedule current session progression
        self.Timer.pause()
        # Update time remaining in session w/ remaining interval time
        self.Timer.update_time_passed_since_start()

        self.change_interval()
        print("SKIP INTERVAL")

    def pause_interval(self):
        """Pauses timer and interval progress"""
        # Unschedule current end event
        self.EventHandler.cancel_event(event_name='change_interval')
        # Unschedule current session progression
        self.Timer.pause()
        # Pause current song
        self.Intervals[self.interval_loop].pause()

    def resume_interval(self):
        """Begings timer and interval progress from pause"""
        # Start song
        self.Intervals[self.interval_loop].resume()

        # Reschedule interval transition
        change_interval_event = Clock.schedule_once(self.change_interval, self.Timer.get_event_time_remaining())
        print("INTERVAL TIME REMAINING: {}".format(self.Timer.get_event_time_remaining()))
        self.EventHandler.schedule_event(event=change_interval_event, event_name='change_interval')

        # Reschedule session progress event
        self.Timer.start()
        print("RESUME INTERVAL")

    def is_final_interval(self):
        """Returns True if current intervla is the last one of the session"""
        return True if self.interval_loop == (self.num_of_work_intervals * 2 - 1) else False

    def skip_track(self):
        """Skips currently playing track and does not effect timer"""
        self.Intervals[self.interval_loop].skip_track()

    def end_session(self):
        """Resets values for session object"""
        self.end_interval()
        self.reset_values()
        self.parent.ids['session_screen'].end_current_session()

    def reset_values(self):
        self.Timer.reset_values()
        self.EventHandler.clear_all_events()
        self.interval_loop = 0

    def get_session_total_time(self):
        """Returns the total duration (in seconds) of the session"""
        return (self.interval_duration['work'] * self.num_of_work_intervals +
                self.interval_duration['rest'] * (self.num_of_work_intervals - 1) +
                self.interval_duration['long_rest'])

    def generate_local_playlist_object(self, file_paths="", playlist_type=""):
        """Add a LocalPlaylist to the session's playlist list"""
        self.playlist[playlist_type] = LocalPlaylist(paths=file_paths)

    def generate_brain_fm_playlist(self):
        """Adds BrainFM Playlists to the sessions playlist list"""
        self.playlist = dict.fromkeys(self.playlist, BrainFMPlaylist(browser=self.driver))

    def generate_spotify_playlist(self, username='', password=''):
        """Adds Spotify Playlists to the session playlist list"""
        self.playlist = dict.fromkeys(self.playlist, SpotifyPlaylist(self.driver))

    def set_intervals_per_session(self, num_of_intervals):
        """Sets value of the number of intervals in the session"""
        self.num_of_work_intervals = int(num_of_intervals)

    def initialize_session_intervals(self):
        """Generate session's intervals"""
        # generate list of interval types ['work', 'rest', 'work', ... 'long_rest']
        interval_types = generate_session_structure(self.num_of_work_intervals)
        # Create intervals
        for index, interval_type in enumerate(interval_types):
            self.Intervals[index] = Interval(duration=self.interval_duration[interval_type],
                                             playlist=self.playlist[interval_type],
                                             style=interval_type)
        # Set duration of session
        self.Timer.set_total_time(self.get_session_total_time())

    def create_driver(self, submission_type, username, password):
        if submission_type == 'BrainFM':
            self.driver = BrainFMBrowser(username=username, password=password)
        elif submission_type == 'Spotify':
            self.driver = SpotifyPlaybackDevice(username=username, password=password)

    def has_valid_credentials(self):
        if isinstance(self.driver, BrainFMBrowser):
            if self.driver.try_login():
                return True
        elif isinstance(self.driver, SpotifyPlaybackDevice):
            if self.driver.has_valid_credentials():
                return True
        return False


