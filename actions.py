from pathlib import Path
import datetime
import pandas


class Action:
    # Directory locations for logging
    root_dir = Path.cwd()
    img_dir = root_dir / 'local' / 'images'
    log_dir = root_dir / 'local' / 'logs'

    def __init__(self, plant_ids=None):
        if not plant_ids:
            raise Exception('Action must have a plant id')
        # There can be multiple plant id's, actions can affect multiple plants
        self.plant_ids = plant_ids

    def on(self):
        raise NotImplementedError

    def off(self):
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
