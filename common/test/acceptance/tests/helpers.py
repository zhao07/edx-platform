"""
Test helper functions.
"""
from path import path


def load_data_str(rel_path):
    """
    Load a file from the "data" directory as a string.
    `rel_path` is the path relative to the data directory.
    """
    full_path = path(__file__).abspath().dirname() / "data" / rel_path
    with open(full_path) as data_file:
        return data_file.read()
