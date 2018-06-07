import datetime
import serial
# Repo specific imports
import util


class Action:
    # Default columns for an action csv
    cols = ['name', 'time']
    name = '-'

    def __init__(self, campo=None):
        assert campo, 'Action must include a campo'
        # There can be multiple plants per campo
        self.plants = list(campo.list_plants()['id'].values)

    @util.timer
    def log(self, **kwargs):
        new_row_dict = kwargs
        new_row_dict['name'] = self.name
        # Make new row entry in each of the plant files
        for plant in self.plants:
            util.save_row(plant, new_row_dict)


class RelayAction(Action):
    # Serial communication defaults for Arduino (see .ino file)
    port = '/dev/'
    baud = 9600
    available_relays = ['pump', 'vlight', 'flight']
    serial_command_dict = {'pump_on': 'a',
                           'pump_off': 'b',
                           'vlight_on': 'c',
                           'vlight_off': 'd',
                           'flight_on': 'e',
                           'flight_off': 'f',
                           }

    def __init__(self, campo=None):
        super(self, RelayAction).__init__(campo)
        self.on_timer = None
        self.timedelta = None

    def on(self, relay=None):
        assert relay in self.available_relays, f'Relay {relay} not in list of available relays'
        self.on_timer = datetime.datetime.now()
        self.serial_command(relay + '_on', state='on')

    def off(self, relay=None):
        assert relay in self.available_relays, f'Relay {relay} not in list of available relays'
        self.timedelta = self.on_timer - datetime.datetime.now()
        self.serial_command(relay + '_off', state='off')

    def serial_command(self, command, **kwargs):
        com = self.serial_command_dict[command]
        assert com, f'Serial command {com} not found'
        with serial.Serial(self.port, self.baud) as ser:
            ser.write(com.encode())
        kwargs['serial_command'] = command
        self.log(kwargs)


class Image(Action):
    name = 'image'

    # action: take image
    # time taken, resolution, reference id to plant
    # feed through aging network, get age