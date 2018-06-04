from pathlib import Path
import datetime
import pandas
from campo import Campo, load_csv

class Action:
    # Directory locations for logging
    root_dir = Path.cwd()
    img_dir = root_dir / 'local' / 'images'
    log_dir = root_dir / 'local' / 'logs'

    # Default columns for an action csv
    cols = ['name', 'time']

    def __init__(self, campo=None):
        assert campo, 'Action must include a campo'

        # There can be multiple plants per campo
        self.plants = list(campo.list_plants()['id'].values)

        for plant in self.plants:
            plant_df = load_csv(plant, self.log_dir, self.cols)

    def on(self):


        raise NotImplementedError

    def off(self):
        datetime.timedelta(minutes=15)
        raise NotImplementedError

    def log(self):
        time = datetime.datetime.now()
        pass
        # Create entry in plant_id csv file with action information


class Image(Action):
    name = 'image'

    # action: take image
    # time taken, resolution, reference id to plant
    # feed through aging network, get age


class Fan(Action):
    name = 'fan'

    # boolean state: turn fan on or off
    # action: turn fan on for X minutes
    # turn fan on until temperature reaches something?


class Water(Action):
    name = 'water'

    # turn on water pump for X minutes
    # turn on water pump until humidity measures something?


class Light(Action):
    name = 'light'

    # boolean state: turn light on or off
    # type of light: vegetation vs flowering
    # duration
