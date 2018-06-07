import argparse
import sched
import time, datetime
# Repo specific imports
import util
from campo import Campo
from actions import Action

if __name__ == '__main__':
    # Arguments determine run behavior
    parser = argparse.ArgumentParser(description='Campo AI Microgreen Grower')
    parser.add_argument('-c', '--campo', type=str, dest='campo', default=None,
                        help='(str) name of the campo')
    parser.add_argument('-p', '--plant', type=str, dest='plant', default=None,
                        help='(str) name of the new plant to add')
    parser.add_argument('-a', '--action', type=str, dest='action', default=None,
                        help='(str) name of the action, must be one of [image, fan, water, light]')
    args = parser.parse_args()

    # Check to make sure required arguments
    assert args.campo, 'Run command must specify a campo'
    assert args.action, 'Run command must specify an action'
    assert args.action in ['image', 'fan', 'water', 'light']

    # Scheduler will use datetime to get time, and time.sleep in between scheduled events
    s = sched.scheduler(timefunc=datetime.datetime.now, delayfunc=time.sleep)

    # Set the campo for all future action instances
    Action.campo = Campo(filename=args.campo)
