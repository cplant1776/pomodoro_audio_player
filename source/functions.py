# Standard Library Imports
import mutagen
import os
from os.path import split
from random import shuffle
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
from selenium import webdriver
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.firefox.options import Options as FirefoxOptions

# Local Imports

WINDOWS_OS = ['win32', 'cygwin']
MAC_OS = ['darwin', 'os2', 'os2emx']
LINUX_OS = ['linux', 'linux2']


def get_playlist_song_titles(file_paths):
    result = []
    for p in file_paths:
        file = mutagen.File(p, easy=True)
        if 'title' in file:
            # Append title if exists
            result.append(file['title'][0])
        else:
            # Append filename
            head, tail = split(p)
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


def create_hide_spotify_window_thread():
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
