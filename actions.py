import datetime
import serial
# Repo specific imports
import util
from campo import Campo


class Action:
    # Default columns for an action csv
    cols = ['name', 'time']
    name = '-'

    # Serial communication defaults for Arduino (see .ino file)
    port = '/dev/'
    baud = 9600
    serial_command_dict = {'pump_on': 'a',
                           'pump_off': 'b',
                           'vlight_on': 'c',
                           'vlight_off': 'd',
                           'flight_on': 'e',
                           'flight_off': 'f',
                           }

    def __init__(self, campo=None):
        assert campo, 'Action must include a campo'
        # There can be multiple plants per campo
        self.plants = list(campo.list_plants()['id'].values)

    def serial_command(self, command):
        com = self.serial_command_dict[command]
        assert com, f'Serial command {com} not found'
        with serial.Serial(self.port, self.baud) as ser:
            ser.write(com.encode())
        self.log(relay=command)

    @util.timer
    def log(self, **kwargs):
        new_row_dict = kwargs
        new_row_dict['name'] = self.name
        # Make new row entry in each of the plant files
        for plant in self.plants:
            util.save_row(plant, new_row_dict)


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
