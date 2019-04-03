class Interval:
    """A container for playlists"""
    def __init__(self, duration=0, playlist=None, style=None):

        self.playlist = playlist
        self.duration = duration
        self.style = style

    def start(self):
        # Start next song
        self.playlist.start(style=self.style)
        print("Start interval")

    def stop(self):
        self.playlist.stop()
        print("Stop interval")

    def pause(self):
        # Pause playlist
        self.playlist.pause()
        print("Pause interval")

    def resume(self):
        self.playlist.resume()
        print("Resume interval")

    def skip_track(self):
        self.playlist.skip_track()
        print("Skipping track....")
