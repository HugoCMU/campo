import datetime
import PiCamera
import util


def image(format='jpeg'):
    image_name = datetime.datetime.now().strftime('%y-%m-%d__%H-%M-%S')
    save_path = str(util.img_dir / image_name)
    with PiCamera() as cam:
        cam.capture(save_path, format=format)
