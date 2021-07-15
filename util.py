# This file holds various utility functions.

import os
import sys

quiet = False

def print_info(message):
    """
    Prints informational content to the console.
    """
    if not quiet:
        print(message)


def fatal_error(message):
    """
    Exits the program with the given error message.
    """
    sys.exit("ERROR: %s" % message)


def assert_dir_exists(directory):
    """
    Checks if the given directory exists. If it doesn't,
    then the program is terminated.
    """
    if not os.path.isdir(directory):
        fatal_error("Directory '%s' doesn't exist." % directory)


def assert_dirs_exist(*directories):
    """
    Checks if the given directories exist. If any doesn't,
    then the program is terminated.
    """
    for directory in directories:
        assert_dir_exists(directory)


def assert_file_exists(filepath):
    """
    Checks if the given filepath exists. If it doesn't,
    then the program is terminated.
    """
    if not os.path.exists(filepath):
        fatal_error("File '%s' doesn't exist." % filepath)


def read_c_ascii_string(buff, offset):
    """
    Reads a C-style (null-terminated) string from a buffer decoded as ASCII.
    """
    s = ""
    while buff[offset] != 0:
        s += chr(buff[offset])
        offset += 1
    return s


def to_c_ascii_string(value):
    """
    Converts a Python string to a C-style (null-terminated) ASCII bytearray.
    """
    s = bytearray(value, 'ASCII')
    s.append(0)
    return s
