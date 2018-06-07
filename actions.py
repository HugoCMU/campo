import datetime
import serial
# Repo specific imports
import util


class Action:
    # Default campo for actions
    campo = None

    # Default columns for an action csv
    cols = ['name', 'time']
    name = '-'

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

    def __init__(self, action):
        assert self.campo, 'Set campo before creating any action objects'
        # There can be multiple plants per campo
        self.plants = list(self.campo.list_plants()['id'].values)

        # Choose proper action function
        action_func = getattr(self, action['name'], None)
        assert isinstance(action_func, function), 'Could not find action in action function dictionary'

    def water(self, **kwargs):
        start_time = kwargs.get('start_time', None)
        duration = kwargs.get('duration', None)
        assert all([start_time, duration]), 'Action function missing arguments'

    def light(self, **kwargs):
        start_time = kwargs.get('start_time', None)
        duration = kwargs.get('duration', None)
        type = kwargs.get('type', None)
        assert all([start_time, duration, type]), 'Action function missing arguments'

    def image(self, **kwargs):
        raise NotImplementedError

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

    @util.timer
    def log(self, **kwargs):
        new_row_dict = kwargs
        new_row_dict['name'] = self.name
        # Make new row entry in each of the plant files
        for plant in self.plants:
            util.save_row(plant, new_row_dict)