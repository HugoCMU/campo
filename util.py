from pathlib import Path
import pandas as pd

"""
Contains common utilities and variables used throughout repo.
"""

# Directory locations for data storage and logging
root_dir = Path.cwd()
img_dir = root_dir / 'local' / 'images'
log_dir = root_dir / 'local' / 'logs'


def make_sure_csv(filename):
    """
    Makes sure that a given filename is a valid csv
    :param filename: (str) filename to check
    :return: filename with .csv ending
    """
    if filename[:-4] != '.csv':
        return filename + '.csv'
    return filename


def load_csv(filename, cols=None):
    """
    Loads a given csv filename into memory as a Pandas Dataframe
    :param filename: (str) file to load
    :param cols: [str,] default columns if file is not found
    :return: (dataframe) loaded csv file
    """
    assert isinstance(filename, str), 'Filename must be a string'
    file = log_dir / make_sure_csv(filename)
    if not file.exists():
        assert cols, 'Default columns must be provided if file does not exist'
        pd.DataFrame(columns=cols).to_csv(str(file), index=False)
    return pd.read_csv(str(file))
