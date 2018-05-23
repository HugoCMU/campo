from pathlib import Path
import datetime
import functools


def log(func):
    """
    Log decorator creates log files for event functions
    :param func:
    :return:
    """

    @functools.wraps(func)
    def _(*args, **kwargs):
        time = datetime.datetime.now()
        result = func(*args, **kwargs, time=time)
        if not result:
            raise Exception()
        print(result + "  " + str(time))
    return _


class Plant:
    # Directory locations for logging
    root_dir = Path.cwd()
    img_dir = root_dir / 'local' / 'images'
    log_dir = root_dir / 'local' / 'logs'

    # Default values for event functions can be changed

    def __init__(self, name):
        self.name = name
        self.pot = None
        self.soil = None
        self.last_watered = None

    @log
    def water(self, duration, **kwargs):
        self.last_watered = kwargs.get('time') + duration
        return f'Watering {self.name} for {duration}'

    @log
    def plant(self, pot, soil, **kwargs):
        self.pot = pot
        self.soil = soil
        return f'Planting {self.name} in {pot} with {soil}'

    @log
    def image(self):
        pass


if __name__ == '__main__':
    cactus = Plant('prickly')
    cactus.plant('pot1', 'soilmix1')
    cactus.water(datetime.timedelta(minutes=15))
