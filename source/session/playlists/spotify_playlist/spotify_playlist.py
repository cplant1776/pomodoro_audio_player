# Standard Library Imports


# Third Party Imports
from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from spotipy import util


# Local Imports
from source.session.playlists.playlist import Playlist
from source.session.playlists.spotify_playlist.spotify_authentication import SpotifyAuthenticator


# =========================
# CONSTANTS
# =========================


class SpotifyPlaylist(Playlist):
    """Container for SpotifyBrowser"""
    def __init__(self, playback_device):
        super().__init__()
        self.playback_device = playback_device
        self.current_mode = 'work'

    def start(self):
        self.change_mode()

    def stop(self):
        self.playback_device.stop()

    def pause(self):
        self.playback_device.pause()

    def resume(self):
        self.playback_device.resume()

    def skip_track(self):
        self.playback_device.skip()

    def change_mode(self):
        """Swaps browser between rest/work/long rest modes"""
        self.playback_device.set_current_mode(self.current_mode)


class SpotifyPlaybackDevice:
    """Spotify playabck device controlled via the Spotify Connect API (spotify_playback_device.html)"""

    def __init__(self, username='', password=''):
        # TODO: implement these functions
        # Get auth token from Spotify1 Authorization API
        self.authenticator = SpotifyAuthenticator(username, password)
        # Launch playlist device in headless browser
        pass

    # TODO: implement these functions
    def toggle_mode(self):
        pass

    def stop(self):
        pass

    def pause(self):
        pass

    def resume(self):
        pass

    def skip_track(self):
        pass

    def set_current_mode(self):
        pass


def create_headless_driver():
    """Returns a headless Firefox webdriver"""
    options = Options()
    # Set browser to headless mode
    options.add_argument("--headless")
    driver = webdriver.Firefox(options=options)
    return driver
