import datetime
from picamera import PiCamera
import gpiozero
import util


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


def on(pin):
    """
    Turn on a digital output device (relay)
    :param pin: (int) pin number
    :return:
    """
    with gpiozero.DigitalOutputDevice(pin=pin) as dev:
        dev.on()


def off(pin):
    """
    Turn off a digital output device (relay)
    :param pin: (int) pin number
    :return:
    """
    with gpiozero.DigitalOutputDevice(pin=pin) as dev:
        dev.off()


if __name__ == '__main__':
    print('Testing camera.py ...')
    image()
