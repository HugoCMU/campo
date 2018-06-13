import argparse
import sched
import time, datetime
# Repo specific imports
import util
# from campo import Campo
# from actions import Action
import camera

if __name__ == '__main__':
    # Arguments determine run behavior
    parser = argparse.ArgumentParser(description='Campo AI Microgreen Grower')
    parser.add_argument('-c', '--campo', type=str, dest='campo',
                        default='test_campo.csv', help='(str) name of the campo')
    parser.add_argument('-s', '--sched', type=str, dest='sched',
                        default='test.csv', help='(str) name of the schedule to use')
    args = parser.parse_args()

    # # Set the campo for all future action instances
    # Action.campo = Campo(filename=args.campo)

    # Scheduler will use datetime to get time, and time.sleep in between scheduled events
    s = sched.scheduler(timefunc=datetime.datetime.now, delayfunc=time.sleep)
    #
    # # Unpack schedule yaml
    # for action_dict in util.load_schedule(args.sched)['actions']:
    #     # Create action instance and add it to the scheduler
    #     a = Action(action_dict, schedule=s)

    # Add camera images (every hour) to schedule
    for hour in range(0, 23):
        s.enterabs(time=datetime.datetime.combine(datetime.date.today(), datetime.time(hour=hour)),
                   priority=1,
                   action=camera.image())
        # argument='vlight_on',
        # kwargs={'action': 'light', 'type': type})

    # Run until all actions have been completed
    while not s.empty():
        s.run()
