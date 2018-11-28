from kivy.core.audio import SoundLoader
from random import shuffle
from kivy.clock import Clock
from random import shuffle

from time import strftime

from .timer import Timer
from .eventhandler import EventHandler


NUM_OF_WORK_INTERVALS = 4
NUM_OF_REST_INTERVALS = 3


class Session:
    def __init__(self):
        self.interval_duration = {'work': -1, 'rest': -1, 'long_rest': -1}

        self.playlist = {'work': LocalPlaylist(), 'rest': LocalPlaylist(), 'long_rest': LocalPlaylist()}

        self.Intervals = {}
        self.interval_loop = 1

        self.Timer = Timer()
        self.EventHandler = EventHandler()

    def generate_playlist(self, file_paths="", playlist_type=""):
        self.playlist[playlist_type] = LocalPlaylist(paths=file_paths)

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

    def initialize_session_intervals(self):
        # Create all 8 intervals for the session (W-R-W-R-W-R-W-LR)
        self.Intervals.update(dict.fromkeys([1, 3, 5, 7], Interval(duration=self.interval_duration['work'],
                                                                   playlist=self.playlist['work'])))
        self.Intervals.update(dict.fromkeys([2, 4, 6], Interval(duration=self.interval_duration['rest'],
                                                                playlist=self.playlist['rest'])))
        self.Intervals[8] = Interval(duration=self.interval_duration['long_rest'],
                                     playlist=self.playlist['rest'])

        self.Timer.set_total_time(self.get_session_total_time())

    def start_next_interval(self):
        # Start interval
        self.Intervals[self.interval_loop].start()
        # Set event timer to length of interval
        self.Timer.set_event_duration(self.Intervals[self.interval_loop].duration)
        # Reset event time passed
        self.Timer.reset_event_time_passed()
        # Star session timer
        self.Timer.start()

        # Schedule event to end current interval
        end_interval_event = Clock.schedule_once(self.end_interval,
                                                 self.Timer.event_duration)
        self.EventHandler.schedule_event(event=end_interval_event, event_name='end_interval')

    def end_interval(self, *args):
        print("{} - Execute: {}".format(strftime('%X'), "end_interval"))

        self.Intervals[self.interval_loop].stop()
        # Pause session timer
        self.Timer.pause()

        # If final interval, end the session
        if self.interval_loop == 8:
            self.end_session()
        else:
            self.interval_loop += 1

        print("Start Interval " + str(self.interval_loop))

        self.start_next_interval()

    def skip_interval(self):
        # Unschedule current end event
        self.EventHandler.cancel_event(event_name='end_interval')
        # Unschedule current session progression
        self.Timer.pause()
        # Update time remaining in session w/ remaining interval time
        self.Timer.update_time_passed_since_start()

        self.end_interval()
        print("end interval")

    def pause_interval(self):
        # Unschedule current end event
        self.EventHandler.cancel_event(event_name='end_interval')
        # Unschedule current session progression
        self.Timer.pause()
        # Pause current song
        self.Intervals[self.interval_loop].pause()

    def resume_interval(self):
        # Start song
        self.Intervals[self.interval_loop].resume()

        # Reschedule interval transition
        end_interval_event = Clock.schedule_once(self.end_interval, self.Timer.get_event_time_remaining())
        print("INTERVAL TIME REMAINING: {}".format(self.Timer.get_event_time_remaining()))
        self.EventHandler.schedule_event(event=end_interval_event, event_name='end_interval')

        # Reschedule session progress event
        self.Timer.start()
        print("RESUME INTERVAL")

    def end_session(self):
        print("SESSION END")
        quit()

    def get_session_total_time(self):
        return (self.interval_duration['work'] * NUM_OF_WORK_INTERVALS +
                self.interval_duration['rest'] * NUM_OF_REST_INTERVALS +
                self.interval_duration['long_rest'])


class Interval:
    def __init__(self, duration=0, playlist=None):

        self.playlist = playlist
        self.duration = duration

        self.Timer = Timer()
        self.EventHandler = EventHandler()

    def start(self):
        self.play_next_song()

    def pause(self):
        # Unschedule event that ends current song
        self.EventHandler.cancel_event(event_name='end_song')
        # Pause playlist
        self.playlist.pause()
        # Stop timer
        self.Timer.pause()

        print("Pause interval")

    def resume(self):
        # Reload song and start playing
        self.playlist.resume(position=self.Timer.event_time_passed)
        # Start timer again
        self.Timer.start()

        # Schedule event to transition to next song
        end_song_event = Clock.schedule_once(self.stop,
                                             self.Timer.get_event_time_remaining())
        self.EventHandler.schedule_event(event=end_song_event, event_name='end_song')

        # Reset seek position
        print("resume song")

    def stop(self, *args):
        print("{} - Execute: {}".format(strftime('%X'), "end_song"))
        self.playlist.stop_current_song()
        self.EventHandler.cancel_event(event_name='end_song')
        self.Timer.pause()

    def set_current_song_event_length(self):
        # Reset event timer
        self.Timer.reset_event_time_passed()
        # Set event duration to song duration
        self.Timer.set_event_duration(self.playlist.get_current_song_length())

    # MODIFY INTERVAL TO JUST START/STOP PLAYLIST
    # MAKE PLAYLIST HANDLE START/STOPPING SONG

    def play_next_song(self):
        # Start next song
        self.playlist.play_next_song()
        # Set event duration
        self.set_current_song_event_length()

        # Start the song timer
        self.Timer.start()

        # Schedule event to end song
        end_song_event = Clock.schedule_once(self.stop,
                                             self.playlist.get_current_song_length())
        self.EventHandler.schedule_event(event=end_song_event, event_name='end_song')


class LocalPlaylist:
    def __init__(self, paths=""):
        # Create randomized track list and load them for use
        self.tracks = []
        self.populate_tracks(paths)
        self.randomize_tracks()
        self.load_tracks_into_memory()

        self.current_index = -1

    def populate_tracks(self, paths):
        # Create list of tracks
        for path in paths:
            self.tracks.append(LocalSong(path))

    def randomize_tracks(self):
        # Shuffle tracks in random order
        shuffle(self.tracks)

    def load_tracks_into_memory(self):
        for track in self.tracks:
            track.load()
            track.seek(0)

    def play_next_song(self):
        # Refill playlist if needed
        if self.no_more_tracks():
            self.restart_playlist()
        # Play next track in playlist
        self.tracks[self.current_index].play()

    def stop_current_song(self):
        self.tracks[self.current_index].stop()

    def no_more_tracks(self):
        if self.current_index == len(self.tracks):
            self.current_index = 0
            return True
        else:
            self.current_index += 1
            return False

    def restart_playlist(self):
        self.current_index = 0

    def get_current_song_length(self):
        return self.tracks[self.current_index].get_length()

    def pause(self):
        self.tracks[self.current_index].stop()

    def resume(self, position=1):
        # Start playback and jump to paused position
        self.tracks[self.current_index].play()
        self.tracks[self.current_index].seek(position)


class LocalSong:
    def __init__(self, path=None):
        self.path = path
        self.song = None

    def load(self):
        if self.song is None:
            self.song = SoundLoader.load(self.path)

    def play(self):
        print("playing {}".format(self.path))
        # sleep(0.5)
        if self.song.status == 'stop':
            self.song = SoundLoader.load(self.path)
            pass
            self.song.play()

    def stop(self):
        if self.song.status != 'stop':
            self.song.stop()

    def seek(self, position):
        self.song.seek(position)

    def get_length(self):
        return self.song.length






