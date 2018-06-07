import functools
import datetime
from pathlib import Path
import yaml
import pandas as pd

"""
Contains common utilities and variables used throughout repo.
"""

# Directory locations for data storage and logging
root_dir = Path.cwd()
img_dir = root_dir / 'local' / 'images'
log_dir = root_dir / 'local' / 'logs'
sched_dir = root_dir / 'local' / 'sched'


def load_schedule(schedule):
    """
    Loads a schedule yaml into a nested dictionary of actions
    :param schedule: (str) yaml file
    :return:
    """
    path = sched_dir / check_extension(schedule, '.yaml')
    return yaml.load(open(str(path), 'r'))


def check_extension(filename, ext):
    """
    Makes sure that a given filename extension is valid
    :param filename: (str) filename to check
    :param ext: (str) extension to check for
    :return: filename with proper ending
    """
    if filename[-len(ext):] != ext:
        return filename + ext
    return filename


def load_csv(filename, cols=None):
    """
    Loads a given csv filename into memory as a Pandas Dataframe
    :param filename: (str) file to load
    :param cols: [str,] default columns if file is not found
    :return: (dataframe) loaded csv file
    """
    assert isinstance(filename, str), 'Filename must be a string'
    file = log_dir / check_extension(filename, '.csv')
    if not file.exists():
        assert cols, 'Default columns must be provided if file does not exist'
        pd.DataFrame(columns=cols).to_csv(str(file), index=False)
    return pd.read_csv(str(file))


def save_row(filename, row_dict, df=None):
    """
    Appends a new row of data to the given file
    :param filename: (str) file to save to
    :param row_dict: (dict) dictionary of columns:values
    :param df: (dataframe) file if already laded
    :return: new dataframe with added plant
    """
    new_row = pd.DataFrame(row_dict, index=[1])
    df = load_csv(filename) if df is None else df
    df = df.append(new_row, ignore_index=True, sort=False)
    df.to_csv(str(log_dir / filename), index=False)
    return df


def timer(func):
    """
    Gives the time as a kwarg to the function
    :param func:
    :return:
    """

    @functools.wraps(func)
    def _(*args, **kwargs):
        time = datetime.datetime.now()
        return func(*args, **kwargs, time=time)

    return _


if __name__ == '__main__':
    # Test loading schedule
    a = load_schedule('test.yaml')
    print(a)
