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

        # self.work_playlist = []
        # self.rest_playlist = []
        # self.long_rest_playlist = []
        self.current_playlist = []

        self.interval = None
        self.interval_loop = 1

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
        self.current_playlist[8] = self.long_rest_playlist

        self.start_interval()

    def start_interval(self):
        self.interval = Interval(playlist=self.current_playlist[self.interval_loop])
        self.interval.start()
        self.end_interval_event = Clock.schedule_once(self.end_interval, self.duration[self.interval_loop])

    def end_interval(self, dt=0):
        self.interval.stop()
        if self.interval_loop == 8:
            self.end_session()
        else:
            self.interval_loop += 1
        self.start_interval()
        print("Start Interval " + str(self.interval_loop))

    def pause_interval(self):
        self.end_interval_event.cancel()
        self.interval.pause_song()
        self.interval_time_elapsed = int(time() - self.interval.start_time)
        print("pause_interval")

    def resume_interval(self):
        self.interval.resume_song()
        self.interval.start_time = time()

        # Reschedule interval transition
        interval_time_remaining = int(self.duration[self.interval_loop] - self.interval_time_elapsed)
        self.end_interval_event = Clock.schedule_once(self.end_interval, interval_time_remaining)
        print("start_interval")

    def end_session(self):
        print("winwinwinnomatterwhat")
        quit()


class Interval:
    def __init__(self, playlist=[]):
        self.full_playlist = playlist
        self.playlist = [i for i in playlist]
        self.start_time = time()

        self.current_song_path = None
        self.next_song_path = None

        self.song_start_time = None
        self.song_time_elapsed = None

        self.playing_song = None
        self.end_song_event = None

    def start(self):
        self.next_song_path = self.pop_song_from_playlist()
        self.play_next_song()

    def pop_song_from_playlist(self):
        result = self.playlist.pop()
        if not self.playlist:
            self.loop_playlist()
        return result

    def loop_playlist(self):
        self.playlist = [i for i in self.full_playlist]

    def play_current_song(self):
        self.playing_song = SoundLoader.load(self.current_song_path)
        self.playing_song.play()

    def play_next_song(self):
        # Make next song the current song and pop the next song
        self.current_song_path, self.next_song_path = self.next_song_path, self.pop_song_from_playlist()

    #     start song
        self.play_current_song()
    #     set up play_next_song to trigger after current song duration
        self.end_song_event = Clock.schedule_once(self.end_playing_song, int(self.playing_song.length))

    def end_playing_song(self, dt=0):
        self.play_next_song()

    def pause_song(self):
        # Unschedule event to transition to next song
        self.end_song_event.cancel()
        # Save current song position for resume
        self.song_time_elapsed = int(self.playing_song.get_pos())
        # Stop playing
        self.playing_song.stop()
        print("Pause song")

    def resume_song(self):
        # Reload song and start playing
        self.play_current_song()
        # Jump to pause position
        self.playing_song.seek(self.song_time_elapsed)
        # Schedule event to transition to next song
        self.end_song_event = Clock.schedule_once(self.end_playing_song,
                                                      self.playing_song.length - self.song_time_elapsed)
        # Reset seek position
        self.song_time_elapsed = 0
        print("resume song")

    def stop(self, dt=0):
        print("Changing intervals . . .")
        self.end_song_event.cancel()
        self.playing_song.stop()




