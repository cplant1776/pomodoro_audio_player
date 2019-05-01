# Standard Library Imports
from os import getcwd, remove
import os.path
from pathlib import Path
import re
import requests
from shutil import move
from shutil import which
import socket
import subprocess
from threading import Thread

# Third Party Imports
from kivy.app import App
from kivy.clock import Clock
from selenium import webdriver
from spotipy import util
import spotipy


# Local Imports
from source.functions import create_headless_driver, hide_spotify_window_thread, update_current_playback_info_spotify
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
        self.device_id = None
        self.uri = generate_uris()
        self.uri_shuffled = {'work': False, 'rest': False, 'long_rest': False}
        self.current_mode = 'work'
        self.current_track_uri = self.get_current_track_name()

    def get_current_track_name(self):
        try:
            return self.player.current_playback()['item']['uri']
        except:
            return ''

    def set_device_id(self):
        os_name = socket.gethostname()
        devices = self.player.devices()

        # Return device ID of open spotify client on same PC
        for device in devices['devices']:
            if device['name'].lower() == os_name.lower():
                self.device_id = device['id']
                return

        # If device not found, try to find it locally
        if self.playback_device.attempt_to_open_client_failed():
            # Finally, prompt user for location
            prompt_user_for_spotify_location()
        else:
            self.set_device_id()

    def start(self, style=""):
        print("style: {} - {}".format(style, self.uri[style]))
        self.current_mode = style

        self.set_device_id()
        self.player.start_playback(device_id=self.device_id, context_uri=self.uri[style])
        hide_spotify_window_thread()

        if not self.uri_shuffled[style]:
            self.player.shuffle(True, device_id=self.device_id)

        # Check for track change every 3 seconds
        self.poll_for_changed_track_event = Clock.schedule_interval(self.poll_for_changed_track, 3)

    def stop(self):
        self.pause()

    def pause(self):
        self.player.pause_playback(device_id=self.device_id)
        self.poll_for_changed_track_event.cancel()

    def resume(self):
        self.player.start_playback(device_id=self.device_id)
        self.poll_for_changed_track_event = Clock.schedule_interval(self.poll_for_changed_track, 3)
        hide_spotify_window_thread()

    def skip_track(self):
        self.player.next_track(device_id=self.device_id)
        hide_spotify_window_thread()

    def change_mode(self):
        """Swaps browser between rest/work/long rest modes"""
        self.playback_device.set_current_mode(self.current_mode)

    def poll_for_changed_track(self, *args):
        current_track_uri = self.get_current_track_name()
        print("old track: {}".format(self.current_track_uri))
        print("new track: {}".format(current_track_uri))
        if current_track_uri == self.current_track_uri:
            pass
        else:
            self.current_track_uri = current_track_uri
            update_current_playback_info_spotify()


class SpotifyPlaybackDevice:
    # Spotify playabck device controlled via the Spotify Connect API

    def __init__(self, username='', password=''):
        # Get auth token from Spotify Authorization API
        self.authenticator = SpotifyAuthenticator(username, password)
        # Launch playlist device in headless browser from generated html file

    def has_valid_credentials(self):
        if self.authenticator.generate_authentication_token():
            return True
        else:
            return False

    def update_credentials(self, username='', password=''):
        self.authenticator.update_credentials(username=username, password=password)

    def attempt_to_open_client_failed(self):
        # Try to find spotify client from PATH
        path = which('spotify')
        if path:
            try:
                subprocess.call([path])
                return False
            except FileNotFoundError:
                pass

        # Fall back to default install locations
        user_home = str(Path.home())
        default_locations = [
            os.path.join(user_home, 'AppData', 'Local', 'Microsoft', 'WindowsApps', 'Spotify.exe'),  # Window default
            os.path.join(os.sep, 'snap', 'bin', 'spotify', 'Spotify.sh'),  # Ubuntu/snap default
            os.path.join(os.sep, 'usr', 'bin', 'spotify', 'Spotify.sh'),  # Debian default
            os.path.join(os.sep, 'Applications', 'Spotify', 'Spotify.sh'),  # Mac default 1
            os.path.join(user_home, 'Applications', 'Spotify', 'Spotify.sh')  # Mac default 2
        ]

        if not self.open_from_default_locations(default_locations):
            return True

    @staticmethod
    def open_from_default_locations(default_paths):
        for path in default_paths:
            try:
                subprocess.call([path])
                return True
            except FileNotFoundError:
                pass

        return False


def generate_uris():
    app = App.get_running_app()
    result = {'work': app.root.ids['spotify_playlist_screen'].ids['work_playlist_name'].selected_playlist_uri,
              'rest': app.root.ids['spotify_playlist_screen'].ids['rest_playlist_name'].selected_playlist_uri,
              'long_rest': app.root.ids['spotify_playlist_screen'].ids['long_rest_playlist_name'].selected_playlist_uri}
    # Set default playlists if none were selected (debugging purposes)
    if result['work'] == '':
        result = {'work': 'spotify:user:spotify:playlist:37i9dQZF1DWWQRwui0ExPn',
                  'rest': 'spotify:user:spotify:playlist:37i9dQZF1DX3Ogo9pFvBkY',
                  'long_rest': 'spotify:user:1259054860:playlist:5dEIAWS7FNY5ZKMKPHSQkw'}
    return result


def prompt_user_for_spotify_location():
    app = App.get_running_app()
    app.root.ids['session_screen'].pop_file_browser()


"""
    Deprecated - web-based playback devices proved too unstable when combined with Selenium.
    Therefore, now using the Spotify Client on the local pc as the playback device.
    
class SpotifyPlaybackDevice:
    # Spotify playabck device controlled via the Spotify Connect API (spotify_playback_device.html)

    def __init__(self, username='', password=''):
        # Get auth token from Spotify Authorization API
        self.authenticator = SpotifyAuthenticator(username, password)
        # Launch playlist device in headless browser from generated html file
        # self.device = create_headless_driver()
        self.device = webdriver.Chrome()

    def has_valid_credentials(self):
        if self.authenticator.generate_authentication_token():
            return True
        else:
            return False

    def open_playback_device(self):
        # Edit html file to include generated authentication code
        self.generate_device_html()
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

    def update_credentials(self, username='', password=''):
        self.authenticator.update_credentials(username=username, password=password)
"""
