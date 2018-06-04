import argparse
# Repo specific imports
import util
from campo import Campo
from actions import Image, Fan, Water, Light

parser = argparse.ArgumentParser(description='Campo AI Microgreen Grower')

# Required
parser.add_argument('-c', '--campo', type=str, dest='campo', default=None, help='(str) name of the campo')

# Campo level
parser.add_argument('-p', '--plant', type=str, dest='plant', default=None, help='(str) name of the new plant to add')

# Action level
parser.add_argument('-a', '--action', type=str, dest='action', default=None,
                    help='(str) name of the action, must be one of [image, fan, water, light]')

if __name__ == '__main__':
    args = parser.parse_args()

    # Check to make sure required arguments
    assert args.campo, 'Run command must specify a campo'
    assert args.action, 'Run command must specify an action'
    assert args.action in ['image', 'fan', 'water', 'light']

    campo = Campo(filename=args.campo)
