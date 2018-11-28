import os.path
from random import shuffle


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
