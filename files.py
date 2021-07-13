import csv

# Cached dictionaries for looking up file information, given
# the original filename or ToadsTool's friendly filename. Yes,
# there is duplicated data in here, but it's fine for now.
from_toadstool = {}
from_original = {}

def get_maps():
    """
    Builds, caches, and fetches the mappings for game files.
    """
    if len(from_toadstool) > 0:
        return from_toadstool, from_original

    with open('game_files.csv') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            from_toadstool[row["toadstool_filepath"]] = row
            from_original[row["original_filepath"]] = row

    return from_toadstool, from_original


def get_original_filepaths():
    """
    Gets the list of all original filepaths.
    """
    _, from_original = get_maps()
    return from_original.keys()


def get_original_filepath(toadstool_filepath):
    """
    Gets the original game's filepath from the ToadsTool filepath.
    """
    from_toadstool, _ = get_maps()
    return from_toadstool[toadstool_filepath]['original_filepath']


def get_toadstool_filepath(original_filepath):
    """
    Gets the ToadsTool filepath from the original game's filepath.
    """
    _, from_original = get_maps()
    return from_original[original_filepath]['toadstool_filepath']


def get_file_id_from_toadstool_filepath(toadstool_filepath):
    """
    Gets the file id from the ToadsTool filepath.
    """
    from_toadstool, _ = get_maps()
    return from_toadstool[toadstool_filepath]['file_id']


def get_file_id_from_original_filepath(original_filepath):
    """
    Gets the file id from the original game's filepath.
    """
    _, from_original = get_maps()
    return from_original[original_filepath]['file_id']
