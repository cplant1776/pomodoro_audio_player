# Standard Library Imports
import mutagen
import os.path
from os.path import split
from random import shuffle
import requests

# Third Party Imports

# Local Imports


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
