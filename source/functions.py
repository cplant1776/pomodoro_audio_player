# Standard Library Imports
import mutagen
import os
from os.path import split
from random import shuffle
import re
import requests
import sys
import time
import tkinter
import win32con
import win32gui


# Third Party Imports
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


def hide_spotify_window():
    user_os = sys.platform

    if user_os in WINDOWS_OS:
        toplist = []
        winlist = []

        def enum_callback(window, results):
            winlist.append((window, win32gui.GetWindowText(window)))

        win32gui.EnumWindows(enum_callback, toplist)
        spotify = [(window, title) for window, title in winlist if 'spotify' in title.lower()]
        try:
            spotify = spotify[0]
        except IndexError:
            return
        win32gui.SetForegroundWindow(spotify[0])
        win32gui.ShowWindow(spotify[0], win32con.SW_MINIMIZE)

    elif user_os in MAC_OS:
        pass

    elif user_os in LINUX_OS:
        pass
