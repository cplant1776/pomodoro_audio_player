import os.path
from random import shuffle
from os.path import split


def get_playlist_song_titles(file_paths):
    result = []
    for p in file_paths:
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

