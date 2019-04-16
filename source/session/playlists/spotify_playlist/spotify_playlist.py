# Standard Library Imports
from os import getcwd, remove
import os.path
import re
import requests
from shutil import move

# Third Party Imports
from kivy.app import App
from selenium import webdriver
from spotipy import util
import spotipy


# Local Imports
from source.functions import create_headless_driver
from source.session.playlists.playlist import Playlist
from source.session.playlists.spotify_playlist.spotify_authentication import SpotifyAuthenticator


# =========================
# CONSTANTS
# =========================
ROOT = os.path.dirname(os.path.realpath(__file__))
PLAYBACK_DEVICE_FILE = os.path.join(ROOT, 'spotify_playback_device.html')


class SpotifyPlaylist(Playlist):
    """Container for SpotifyBrowser"""
    def __init__(self, playback_device):
        super().__init__()
        self.playback_device = playback_device
        self.player = spotipy.Spotify(auth=self.playback_device.authenticator.auth_token)
        self.device_id = self.get_device_id()
        self.uri = self.generate_uris()
        self.current_mode = 'work'

    @staticmethod
    def generate_uris():
        app = App.get_running_app()
        result = {'work': app.root.ids['spotify_playlist_screen'].ids['work_playlist_name'].selected_playlist_uri,
                  'rest': app.root.ids['spotify_playlist_screen'].ids['rest_playlist_name'].selected_playlist_uri,
                  'long_rest': app.root.ids['spotify_playlist_screen'].ids['long_rest_playlist_name'].selected_playlist_uri}
        return result

    def get_device_id(self):
        devices = self.player.devices()
        for device in devices['devices']:
            if device['name'] == 'Web Playback SDK Quick Start Player':
                return device['id']

    def start(self, style=""):
        print("style: {} - {}".format(style, self.uri[style]))
        self.current_mode = style
        self.player.start_playback(device_id=self.device_id, context_uri=self.uri[style])
        self.player.shuffle(True, device_id=self.device_id)

    def stop(self):
        self.pause()

    def pause(self):
        self.player.pause_playback(device_id=self.device_id)

    def resume(self):
        self.player.start_playback(device_id=self.device_id)

    def skip_track(self):
        self.player.next_track(device_id=self.device_id)

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
        # Launch playlist device in headless browser from generated html file
        self.device = create_headless_driver()
        html_file = getcwd() + "//" + PLAYBACK_DEVICE_FILE
        self.device.get("file:///" + html_file)

    def generate_device_html(self):
        pattern = "(const token = ')(.*)(';)"
        temp_file = os.path.join(ROOT, 'tmp.html')

        # Copy line by line to temporary files
        with open(temp_file, "w+") as out:
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
        move(temp_file, PLAYBACK_DEVICE_FILE)
