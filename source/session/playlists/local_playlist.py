from source.session.timer import Timer
from source.session.eventhandler import EventHandler
from random import shuffle
from kivy.clock import Clock
from kivy.core.audio import SoundLoader
from time import strftime
from source.session.playlists.playlist import Playlist


class LocalPlaylist(Playlist):
    """Container for LocalSong objects"""
    def __init__(self, paths=None):
        super().__init__()
        # Fill playlist with tracks from paths
        self.tracks = []
        self.current_index = -1
        self.initialize_tracks(paths)

        self.Timer = Timer()
        self.EventHandler = EventHandler()

    def start(self):
        # Start the song timer
        self.Timer.start()
        self.next_song_sequence()

    def stop(self):
        self.Timer.pause()
        self.end_song()

    def pause(self):
        # Unschedule event that ends current song
        self.EventHandler.cancel_event(event_name='end_song_and_play_next')
        # Pause song
        self.tracks[self.current_index].stop()
        # Stop song timer
        self.Timer.pause()
        print("Pause playlist")

    def resume(self):
        # Start timer again
        self.tracks[self.current_index].resume()
        self.Timer.start()

    def skip_track(self):
        self.end_song_and_play_next()

    def initialize_tracks(self, paths=None):
        # Load LocalSong objects
        self.create_song_objects(paths)
        # Randomize order of songs
        self.randomize_tracks()
        # self.load_tracks_into_memory()

    def create_song_objects(self, paths=None):
        # Create list of LocalSong objects
        for path in paths:
            self.tracks.append(LocalSong(path))

    def randomize_tracks(self):
        # Shuffle tracks in random order
        shuffle(self.tracks)

    def load_tracks_into_memory(self):
        for track in self.tracks:
            track.load()

    def next_song_sequence(self):
        self.update_current_index()
        self.play_next_track()

        # Update Timer with new info
        self.Timer.reset_event_time_passed()
        song_length = self.tracks[self.current_index].get_length()
        self.Timer.set_event_duration(song_length)

        # Schedule end of song event
        end_song_event = Clock.schedule_once(self.end_song_and_play_next,
                                             self.Timer.get_event_time_remaining())
        self.EventHandler.schedule_event(event=end_song_event, event_name="end_song_and_play_next")

    def end_song_and_play_next(self, *args):
        self.end_song()
        self.next_song_sequence()

    def end_song(self):
        print("{} - Execute: {} ==> {}".format(strftime('%X'), "end_song_and_play_next",
                                               self.EventHandler.events['end_song_and_play_next']))
        # Cancel end event if it remains
        if self.EventHandler.events['end_song_and_play_next']:
            self.EventHandler.cancel_event(event_name="end_song_and_play_next")
        self.tracks[self.current_index].stop()

    def play_next_track(self):
        self.tracks[self.current_index].play()

    def update_current_index(self):
        if self.no_more_tracks():
            self.restart_playlist()
        else:
            self.current_index += 1

    def no_more_tracks(self):
        return True if self.current_index == len(self.tracks) else False

    def restart_playlist(self):
        self.current_index = 0


class LocalSong:
    """Directly controls playback of local audio files"""
    def __init__(self, path=None):
        self.path = path
        self.song = None
        self.position = 0

    def load(self):
        self.song = SoundLoader.load(self.path)
        self.song.seek(0)

    def play(self):
        # Load into memory if not already loaded or is stopped
        if self.song is None or self.song.status == 'stop':
            self.load()
        self.song.play()
        print("playing {}".format(self.path))

    def stop(self):
        if self.song.status != 'stop':
            # save song position for resume
            print(self.position)
            self.position = int(self.song.get_pos())
            print(self.position)
            self.song.stop()

    def resume(self):
        if self.song.status == 'stop':
            self.song.play()
            self.seek(position=self.position)

    def seek(self, position):
        self.song.seek(position)

    def get_length(self):
        return self.song.length
