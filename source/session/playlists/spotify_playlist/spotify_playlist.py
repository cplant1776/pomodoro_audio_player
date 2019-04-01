# Standard Library Imports
from os import getcwd, remove
import re
import requests
from shutil import move

# Third Party Imports
from selenium import webdriver
from spotipy import util


# Local Imports
from source.functions import create_headless_driver
from source.session.playlists.playlist import Playlist
from source.session.playlists.spotify_playlist.spotify_authentication import SpotifyAuthenticator


# =========================
# CONSTANTS
# =========================
PLAYBACK_DEVICE_FILE = 'spotify_playback_device.html'


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
        # Get auth token from Spotify Authorization API
        self.authenticator = SpotifyAuthenticator(username, password)
        # Edit html file to include generated authentication code
        self.generate_device_html()
        # Launch playlist device in headless browser from generated httml file
        self.device = create_headless_driver()
        html_file = getcwd() + "//" + PLAYBACK_DEVICE_FILE
        self.device.get("file:///" + html_file)

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

    def generate_device_html(self):
        pattern = "(const token = ')(.*)(';)"

        # Copy line by line to temporary files
        with open("tmp.html", "w+") as out:
            for line in open(PLAYBACK_DEVICE_FILE, 'r'):
                search_result = re.search(pattern, line)
                # If it's the line setting the auth code
                if search_result:
                    old_code = search_result.group(2)
                    out.write(line.replace(old_code, self.authenticator.auth_token))
                else:
                    out.write(line)
        # Replace old file
        remove(PLAYBACK_DEVICE_FILE)
        move('tmp.html', PLAYBACK_DEVICE_FILE)