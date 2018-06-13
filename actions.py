import datetime
import functools
# Repo specific imports
import util
import pi

def eval_times(func):
    @functools.wraps(func)
    def _(*args, **kwargs):
        assert all(k in kwargs for k in ['start_time', 'duration']), 'Action function missing arguments'
        # Evaluate the datetime strings in the schedule
        start_time = eval(kwargs['start_time'])
        duration = eval(kwargs['duration'])
        # Start and stop times are based on current date
        start_time = datetime.datetime.combine(datetime.date.today(), start_time)
        stop_time = start_time + duration
        # Add the updated times to the kwargs
        kwargs['start_time'] = start_time
        kwargs['stop_time'] = stop_time
        kwargs['duration'] = duration
        return func(*args, **kwargs)
    return _


class Action:
    # Default campo for actions
    campo = None

    # Default columns for an action csv
    cols = ['name', 'time']
    name = '-'

    def __init__(self, action_dict, schedule):
        assert self.campo, 'Set campo before creating any action objects'
        self.s = schedule
        # Call proper action function
        action_func = getattr(self, action_dict['name'], None)
        assert callable(action_func), 'Could not find action in action function dictionary'
        action_func(**action_dict)

    @eval_times
    def water(self, **kwargs):
        assert all(k in kwargs for k in ['start_time', 'stop_time']), 'Action function missing arguments'
        # Add pump on and pump off serial commands to scheduler
        self.s.enterabs(time=kwargs['start_time'],
                        priority=1,
                        action=pi.on,
                        kwargs={'action': 'water'})
        self.s.enterabs(time=kwargs['stop_time'],
                        priority=1,
                        action=pi.off,
                        kwargs={'action': 'water'})

    @eval_times
    def light(self, **kwargs):
        assert all(k in kwargs for k in ['start_time', 'stop_time', 'type']), 'Action function missing arguments'
        type = kwargs['type']
        if type == 'veg' or type == 'full':
            # Add pump on and pump off serial commands to scheduler
            self.s.enterabs(time=kwargs['start_time'],
                            priority=1,
                            action=pi.on,
                            kwargs={'action': 'light', 'type': type})
            self.s.enterabs(time=kwargs['stop_time'],
                            priority=1,
                            action=pi.off,
                            kwargs={'action': 'light', 'type': type})

        if type == 'flow' or type == 'full':
            # Add pump on and pump off serial commands to scheduler
            self.s.enterabs(time=kwargs['start_time'],
                            priority=1,
                            action=pi.on,
                            kwargs={'action': 'light', 'type': type})
            self.s.enterabs(time=kwargs['stop_time'],
                            priority=1,
                            action=pi.off,
                            kwargs={'action': 'light', 'type': type})

    @util.timer
    def log(self, **kwargs):
        new_row_dict = kwargs
        new_row_dict['name'] = self.name
        # Make new row entry in each of the plant files
        for plant in self.campo.list_plants():
            util.save_row(plant, new_row_dict)


if __name__ == '__main__':
    print('Running tests for actions.py')
    from campo import Campo
    import sched
    import time

    Action.campo = Campo('test_campo.csv')

    s = sched.scheduler(timefunc=datetime.datetime.now, delayfunc=time.sleep)

    # Unpack schedule yaml
    for action_dict in util.load_schedule('test.yaml')['actions']:
        # Create action instance and add it to the scheduler
        a = Action(action_dict, schedule=s)

    print(s)
