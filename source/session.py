from kivy.core.audio import SoundLoader
from random import shuffle
from kivy.clock import Clock
from copy import deepcopy
from time import time


class Session:
    def __init__(self):
        self.work_interval = 10
        self.rest_interval = 5
        self.long_rest_interval = 15

        self.work_playlist = []
        self.rest_playlist = []
        self.long_rest_playlist = []

        self.current_playlist = []

        self.interval = None
        self.interval_loop = 1
        self.interval_time_elapsed = 0

        self.session_time_passed = 0

    @staticmethod
    def get_songs_string(playlist):
        # extract every other entry (the file name)
        return ''.join(playlist[0::2])

    @staticmethod
    def get_path_list(playlist):
        # get list of song directories in random order
        result = playlist[1::2]
        shuffle(result)
        return result

    def initialize_session(self):
        # Set duration of intervals (W-R-W-R-W-R-W-LR]
        self.duration = dict.fromkeys([1, 3, 5, 7], self.work_interval)
        self.duration.update(dict.fromkeys([2, 4, 6], self.rest_interval))
        self.duration[8] = self.long_rest_interval

        # define each playlist (work, rest, long rest)
        work_queue = self.get_path_list(self.work_playlist)
        rest_queue = self.get_path_list(self.rest_playlist)
        long_rest_queue = self.get_path_list(self.long_rest_playlist)

        # Set playlist for each interval (W-R-W-R-W-R-W-LR]
        self.current_playlist = dict.fromkeys([1, 3, 5, 7], work_queue)
        self.current_playlist.update(dict.fromkeys([2, 4, 6], rest_queue))
        self.current_playlist[8] = long_rest_queue

        # Start interval 1
        self.start_interval()

    def start_interval(self):
        self.interval = Interval(playlist=self.current_playlist[self.interval_loop])
        self.interval.start()
        self.end_interval_event = Clock.schedule_once(self.end_interval, self.duration[self.interval_loop])
        self.session_progress_event = Clock.schedule_interval(self.update_session_progress, 1)

    def update_session_progress(self, *args):
        self.session_time_passed += 1

    def end_interval(self, dt=0):
        self.interval.stop()
        if self.interval_loop == 8:
            self.end_session()
        else:
            self.interval_loop += 1
        self.start_interval()
        print("Start Interval " + str(self.interval_loop))

    def skip_interval(self):
        # Unschedule current end event
        self.end_interval_event.cancel()
        # Unschedule current session progression
        self.session_progress_event.cancel()
        # Update time remaining in session
        self.session_time_passed += self.get_interval_time_remaining()
        self.end_interval()
        print("end interval")

    def pause_interval(self):
        # Unschedule current end event
        self.end_interval_event.cancel()
        # Unschedule current session progression
        self.session_progress_event.cancel()
        # Pause current song
        self.interval.pause_song()
        # Save interval position for resume
        self.interval_time_elapsed = int(time() - self.interval.start_time)
        print("pause_interval")

    def resume_interval(self):
        # Start song
        self.interval.resume_song()
        # Save start time
        self.interval.start_time = time()

        # Reschedule interval transition
        self.end_interval_event = Clock.schedule_once(self.end_interval, self.get_interval_time_remaining())
        # Reschedule session progress event
        self.session_progress_event = Clock.schedule_interval(self.update_session_progress, 1)
        print("start_interval")

    def end_session(self):
        print("winwinwinnomatterwhat")
        quit()

    def get_session_time_remaining(self):
        return int(self.get_session_total_time() - self.session_time_passed)

    def get_interval_time_remaining(self):
        return int(self.duration[self.interval_loop] - self.interval_time_elapsed)

    def get_session_total_time(self):
        return int(self.work_interval*4 + self.rest_interval*3 + self.long_rest_interval)


class Interval:
    def __init__(self, playlist=[]):
        self.full_playlist = playlist
        self.playlist = [i for i in playlist]
        self.start_time = time()

        self.next_song = None
        self.current_song = None

        self.current_song_path = None
        self.next_song_path = None

        self.playing_song = None
        self.end_song_event = None

    def start(self):
        self.next_song = Song(path=self.pop_song_from_playlist())
        self.play_next_song()

    def pop_song_from_playlist(self):
        result = self.playlist.pop()
        if not self.playlist:
            self.loop_playlist()
        return result

    def loop_playlist(self):
        self.playlist = [i for i in self.full_playlist]

    def play_current_song(self):
        self.current_song.load()
        self.current_song.play()

    def play_next_song(self):
        # Make next song the current song and pop the next song
        self.current_song, self.next_song = self.next_song, Song(self.pop_song_from_playlist())

    #     start song
        self.play_current_song()
    #     set up play_next_song to trigger after current song duration
        self.end_song_event = Clock.schedule_once(self.end_current_song,
                                                  int(self.current_song.get_length()))

    def end_current_song(self, dt=0):
        self.play_next_song()

    def pause_song(self):
        # Unschedule event to transition to next song
        self.end_song_event.cancel()
        # Save current song position for resume
        self.current_song.save_position()
        # Stop playing
        self.current_song.stop()
        print("Pause song")

    def resume_song(self):
        # Reload song and start playing
        self.play_current_song()
        # Jump to pause position
        self.current_song.seek()
        # Schedule event to transition to next song
        self.end_song_event = Clock.schedule_once(self.end_current_song,
                                                  self.current_song.time_remaining)
        # Reset seek position
        print("resume song")

    def stop(self, dt=0):
        print("Changing intervals . . .")
        self.end_song_event.cancel()
        self.current_song.stop()


class Song:
    def __init__(self, path=None):
        self.path = path
        self.song = None

        self.time_elapsed = 0
        self.time_remaining = 0

    def load(self):
        self.song = SoundLoader.load(self.path)

    def play(self):
        self.song.play()

    def stop(self):
        self.time_remaining = self.song.length - self.time_elapsed
        self.song.stop()

    def seek(self):
        self.song.seek(self.time_elapsed)

    def save_position(self):
        self.time_elapsed = int(self.song.get_pos())

    def get_length(self):
        return self.song.length






