# Standard Library Imports
import os
from os.path import split
from random import shuffle, randint
import re
import requests
import sys
from threading import Thread
import time
import tkinter
import win32con
import win32gui


# Third Party Imports
from kivy.app import App
from mutagen import File
from selenium import webdriver
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.firefox.options import Options as FirefoxOptions
import stagger


# Local Imports

WINDOWS_OS = ['win32', 'cygwin']
MAC_OS = ['darwin', 'os2', 'os2emx']
LINUX_OS = ['linux', 'linux2']


def get_playlist_song_titles(file_paths):
    result = []
    for path in file_paths:
        tag = stagger.read_tag(path)
        if tag.title:
            # Append title if exists
            result.append(tag.title)
        else:
            # Append filename
            head, tail = split(path)
            result.append(tail)
    result = '\n'.join(result)
    return result


def extract_file_paths(path, filename):
    result = []
    with open(os.path.join(path, filename[0])) as playlist_file:
        # skip 1st line
        next(playlist_file)
        # Parse each line for filename and path
        for line in playlist_file:
            items = line.split(",")
            if line.startswith("#EXT"):
                # filename
                result.append(items[1])
            else:
                # path
                result.append(items[0])
    # remove newline characters from results
    result = [s.strip('\n') for s in result]

    # get list of song directories in random order
    result = result[1::2]
    shuffle(result)
    return result


def generate_session_structure(num_of_work_intervals=4):
    interval_sequence = [None] * int(num_of_work_intervals) * 2
    for i in range(0, int(num_of_work_intervals) * 2, 2):
        interval_sequence[i] = 'work'
        interval_sequence[i + 1] = 'rest'
    interval_sequence[-1] = 'long_rest'
    return interval_sequence


def download_temporary_image(url, destination):
    # Send request to url
    res = requests.get(url, stream=True)
    # Check for valid response then download to temp directory
    if res.status_code == 200:
        with open(destination, 'wb') as f:
            for chunk in res:
                f.write(chunk)


def get_temp_file_path(url):
    name = url.split("/")[-1]
    return os.path.join("tmp", name + ".jpg")


def create_headless_driver():
    """Returns a headless Firefox or Chrome webdriver"""

    try:
        options = ChromeOptions()
        options.headless = True
        # Workaround to set fullscreen since fullscreen argument does not work with headless mode
        options.add_argument(set_to_fullscreen())
        return webdriver.Chrome(options=options)
    #     TODO: Add specific exceptions: no driver, no browser
    except:
        print("Chrome launch failed. Trying Firefox . . .")

    try:
        options = FirefoxOptions()
        options.headless = True
        return webdriver.Firefox(options=options)
    #     TODO: Add specific exceptions: no driver, no browser
    except:
        print("Firefox launch failed. . .")
        # TODO: Add popup for user with what caused the error


def set_to_fullscreen():
    root = tkinter.Tk()
    return "--window-size=1{},{}".format(root.winfo_screenwidth(), root.winfo_screenheight())


def clear_expired_cache():
    local_files = ' '.join(os.listdir())
    regex = re.search("(\.cache-\w*)\s", local_files)

    try:
        cache_path = regex.group(1)
    except AttributeError:  # cache not found
        return

    last_modified = int(os.path.getmtime(cache_path))
    # If cache is more than 1 hour old, delete it
    if int(time.time()) - last_modified > 3600:
        os.remove(cache_path)


def hide_spotify_window_thread():
    t = Thread(target=hide_spotify_window)
    print("Schedule hide spotify thread")
    t.start()


def hide_spotify_window():
    user_os = sys.platform
    print("hide spotify window")

    if user_os in WINDOWS_OS:

        for n in range(10):
            time.sleep(0.15)
            print("hide attempt {}".format(n))
            attempt_succesful = search_for_spotify_window()[1]
            if attempt_succesful:
                break
            else:
                pass

        spotify_window = search_for_spotify_window()[0][0]
        win32gui.SetForegroundWindow(spotify_window)
        win32gui.ShowWindow(spotify_window, win32con.SW_MINIMIZE)
        focus_app_window()

    elif user_os in MAC_OS:
        pass

    elif user_os in LINUX_OS:
        pass


def search_for_spotify_window():
    toplist = []
    winlist = []
    session = App.get_running_app().root.session

    def enum_callback(window, results):
        winlist.append((window, win32gui.GetWindowText(window)))

    def get_spotify_artist_name():
        playback_info = session.Intervals[session.interval_loop].playlist.player.current_playback()
        return playback_info['item']['artists'][0]['name']

    win32gui.EnumWindows(enum_callback, toplist)

    try:
        spotify = [(window, title) for window, title in winlist if 'spotify' in title.lower()]
        spotify = spotify[0]
        print("spotify = {}".format(spotify))
        return spotify, True

    except IndexError:
        artist_name = None

        try:
            while artist_name != get_spotify_artist_name():
                artist_name = get_spotify_artist_name()
            spotify = [(window, title) for window, title in winlist if artist_name.lower() in title.lower()]
            spotify = spotify[0]
            print("IndexError spotify = {}".format(spotify))
            return spotify, True

        except IndexError or TypeError:
            return None, False


def focus_app_window():
    app_window = search_for_app_window()
    if app_window:
        win32gui.SetForegroundWindow(app_window)
    else:
        print("App window not found.")
    # win32gui.ShowWindow(app_window, win32con.SW_MINIMIZE)


def search_for_app_window():
    toplist = []
    winlist = []

    def enum_callback(window, results):
        winlist.append((window, win32gui.GetWindowText(window)))

    win32gui.EnumWindows(enum_callback, toplist)
    app_window = [(window, title) for window, title in winlist if title.lower() == 'pomodoro']

    try:
        app_window = app_window[0][0]
    except IndexError or TypeError:
        return None

    print("app window = {}".format(app_window))
    return app_window


def update_current_playback_info_local(file_path=''):
    data = {}
    tag = stagger.read_tag(file_path)

    if tag.album_artist:
        data['artist'] = tag.album_artist
    elif tag.artist:
        data['artist'] = tag.artist

    if tag.album:
        data['album'] = tag.album
    if tag.title:
        data['title'] = tag.title
    if tag.picture:
        file = File(file_path)
        artwork = file.tags['APIC:'].data
        temp_file = 'tmp/{}.jpg'.format(randint(9999, 9999999))
        with open(temp_file, 'wb') as img:
            img.write(artwork)
        data['artwork'] = temp_file

    update_current_playback_info(data)


def update_current_playback_info_spotify(res=None):
    data = {}

    try:
        data['artist'] = res['item']['album']['artists'][0]['name']
    except KeyError:
        print("spotify api - No artist name found!")

    try:
        data['album'] = res['item']['album']['name']
    except KeyError:
        print("spotify api - No album name found!")

    try:
        data['title'] = res['item']['name']
    except KeyError:
        print("spotify api - No song title found!")

    try:  # Try for smaller image first
        album_art_url = res['item']['album']['images'][1]['url']
    except IndexError:

        try:  # Fallback to larger image
            album_art_url = res['item']['album']['images'][0]['url']
        except IndexError:
            print("spotify api - No album art found!")

    if album_art_url:
        destination_path = get_temp_file_path(album_art_url)
        download_temporary_image(album_art_url, destination_path)
        data['artwork'] = destination_path

    update_current_playback_info(data)


def update_current_playback_info_brainfm():
    screen = App.get_running_app().root.ids['session_screen']
    screen.ids['playback_info_label'].opacity = 0

    data = {'is_brainfm': True}
    update_current_playback_info(data)


def update_current_playback_info(data={}):
    screen = App.get_running_app().root.ids['session_screen']

    # Update artist name
    try:
        screen.playback_artist = data['artist']
    except KeyError:
        screen.playback_artist = 'Unknown Artist'
        print('Artists not found!')

    # Update album name
    try:
        screen.playback_album = data['album']
    except KeyError:
        screen.playback_album = 'Unknown Album'
        print('Album name not found!')

    # Update song name
    try:
        screen.playback_title = data['title']
    except KeyError:
        screen.playback_title = 'Unknown Title'
        print('Title not found!')

    try:
        screen.playback_artwork = data['artwork']
    except KeyError:
        session = App.get_running_app().root.session
        current_playlist_type = App.get_running_app().root.session.Intervals[session.interval_loop].style

        artwork_file = {'work': 'focus-placeholder.jpg',
                        'rest': 'rest-placeholder.jpg',
                        'long_rest': 'long-rest-placeholder.jpg'}

        artwork_path = os.path.join('.', 'assets', 'images', 'album_artwork', artwork_file[current_playlist_type])
        screen.playback_artwork = artwork_path
        print("Artwork not found!")

    try:
        temp = data['is_brainfm']
        screen.ids['playback_info_label'].opacity = 0
    except KeyError:
        screen.ids['playback_info_label'].opacity = 1
