from source.session.timer import Timer
from source.session.eventhandler import EventHandler
from random import shuffle
from kivy.clock import Clock
from kivy.core.audio import SoundLoader
from time import strftime


class LocalPlaylist:
    def __init__(self, paths=""):
        # Create randomized track list and load them for use
        self.tracks = []
        self.current_index = -1

        self.Timer = Timer()
        self.EventHandler = EventHandler()

        self.initialize_tracks(paths)

    def initialize_tracks(self, paths=""):
        self.create_song_objects(paths)
        self.randomize_tracks()
        # self.load_tracks_into_memory()

    def create_song_objects(self, paths):
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

    def start(self):
        # Start the song timer
        self.Timer.start()
        self.play_next_song()

    def stop(self):
        self.Timer.pause()
        self.end_song()

    def skip_track(self):
        self.end_song_and_play_next()

    def play_next_song(self):
        # Refill playlist if needed
        if self.no_more_tracks():
            self.restart_playlist()
        # Play next track in playlist
        self.tracks[self.current_index].play()

        self.Timer.reset_event_time_passed()
        # Set Timer event_duration = song_length
        song_length = self.tracks[self.current_index].get_length()
        self.Timer.set_event_duration(song_length)

        # Schedule end of song playback
        end_song_event = Clock.schedule_once(self.end_song_and_play_next,
                                             self.Timer.get_event_time_remaining())
        self.EventHandler.schedule_event(event=end_song_event, event_name="end_song_and_play_next")

    def end_song(self):
        print("{} - Execute: {} ==> {}".format(strftime('%X'), "end_song_and_play_next", self.EventHandler.events['end_song_and_play_next']))
        # Cancel end event if it remains
        if self.EventHandler.events['end_song_and_play_next']:
            self.EventHandler.cancel_event(event_name="end_song_and_play_next")
        self.tracks[self.current_index].stop()

    def end_song_and_play_next(self, *args):
        self.end_song()
        self.play_next_song()

    def no_more_tracks(self):
        if self.current_index == len(self.tracks):
            self.current_index = 0
            return True
        else:
            self.current_index += 1
            return False

    def restart_playlist(self):
        self.current_index = 0

    def pause(self):
        # Unschedule event that ends current song
        self.EventHandler.cancel_event(event_name='end_song_and_play_next')
        # Pause song
        self.tracks[self.current_index].stop()
        # Stop song timer
        self.Timer.pause()

        print("Pause playlist")

    def resume(self, position=1):
        # Start timer again
        self.Timer.start()

        # Start playback and jump to paused position
        self.tracks[self.current_index].play()
        self.tracks[self.current_index].seek(self.Timer.event_time_passed)

        # Schedule event to transition to next song
        end_song_event = Clock.schedule_once(self.end_song,
                                             self.Timer.get_event_time_remaining())
        self.EventHandler.schedule_event(event=end_song_event, event_name='end_song_and_play_next')

        # Reset seek position
        print("resume playlist")


class LocalSong:
    def __init__(self, path=None):
        self.path = path
        self.song = None

    def load(self):
        self.song = SoundLoader.load(self.path)

    def play(self):
        # Load into memory if not already loaded or is stopped
        if self.song is None or self.song.status == 'stop':
            self.load()

        self.song.play()

        print("playing {}".format(self.path))

    def stop(self):
        if self.song.status != 'stop':
            self.song.stop()

    def seek(self, position):
        self.song.seek(position)

    def get_length(self):
        return self.song.length