import datetime
from picamera import PiCamera
import gpiozero
import util

# Import pins
from aiy.vision.pins import PIN_A, PIN_B, PIN_C

pin_dict = {'water': gpiozero.DigitalOutputDevice(PIN_A, active_high=False),
            'vlight': gpiozero.DigitalOutputDevice(PIN_B, active_high=False),
            'flight': gpiozero.DigitalOutputDevice(PIN_C, active_high=False),
            }


def image(format='jpeg'):
    """
    Takes image using PiCamera module, saves to image directory in util path
    :param format: (str) image format
    :return: None
    """
    image_name = datetime.datetime.now().strftime('%y-%m-%d__%H-%M-%S') + '.' + format
    save_path = str(util.img_dir / image_name)
    with PiCamera() as cam:
        cam.capture(save_path, format=format)
        print(f'Image saved at {save_path}')


def on(action=None):
    """
    Turn on a digital output device (relay)
    :param action:
    :return:
    """
    assert action in pin_dict.keys(), 'action does not exist in pin dictionary'
    pin_dict[action].on()


def off(action=None):
    """
    Turn off a digital output device (relay)
    :param action:
    :return:
    """
    assert action in pin_dict.keys(), 'action does not exist in pin dictionary'
    pin_dict[action].off()


if __name__ == '__main__':
    print('Testing camera.py ...')
    import time

    image()
    while True:
        print('Turning on relays')
        on(action='water')
        on(action='vlight')
        on(action='flight')
        time.sleep(3)
        print('Turning off relays')
        off(action='water')
        off(action='vlight')
        off(action='flight')
        time.sleep(3)
