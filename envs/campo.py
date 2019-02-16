"""Gym environment for campo RL algo."""
import collections
import logging
import os
import gym
import time
import numpy as np
from dxl_py.servos import Servos

# Manually import realsense module
import importlib.util

import pdb

REALSENSE_PATH = os.path.abspath(
    os.path.join(os.path.dirname(os.path.abspath(__file__)), '../../realsense-tcp-module/cameras.py'))
spec = importlib.util.spec_from_file_location("realsense-tcp-module.cameras", REALSENSE_PATH)
realsense_module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(realsense_module)

# Servo config dictionary contains individual per-servo information
SERVO_CONFIG = {
    # 'servo_1': {
    #     'id': 1,
    #     'model': 'mx',
    #     'min': 0,
    #     'max': 4095,
    # },
    'servo_2': {
        'id': 2,
        'model': 'mx',
        'min': 0,
        'max': 4095,
    },
    'servo_3': {
        'id': 3,
        'model': 'mx',
        'min': 0,
        'max': 4095,
    },
}


class CampoEnv(gym.Env):
    """Gym environment for campo."""

    def __init__(self):
        super().__init__()
        self.camera = realsense_module.RealSense(tcp_ip='127.0.0.1', tcp_port=50200)
        time.sleep(1)  # Give camera some time to load data
        self.servos = Servos(
            device_name='/dev/ttyUSB0',
            baudrate=1000000,
            protocol_version=2.0,
            action_bounds=[-1.0, 1.0],
            config=SERVO_CONFIG)
        self.reset_pose = {
            # 'servo_1': np.random.uniform(low=-1.0, high=1.0),
            'servo_2': np.random.uniform(low=-1.0, high=1.0),
            'servo_3': np.random.uniform(low=-1.0, high=1.0),
        }

    def _get_obs(self):
        obs = collections.OrderedDict()
        # Fetch latest information from camera
        obs['color_image'] = self.camera.color_im
        obs['depth_image'] = self.camera.depth_im
        obs['timestamp'] = self.camera.timestamp
        obs['color_intrinsics'] = self.camera.color_intr
        obs['depth_intrinsics'] = self.camera.depth_intr
        obs['depth2color_extrinsic'] = self.camera.depth2color_extr
        logging.debug('STEP')
        logging.debug('timestamp %s' % self.camera.timestamp)
        logging.debug('color image   %s   %s' % (self.camera.color_im.dtype, self.camera.color_im.shape))
        logging.debug('depth image   %s   %s' % (self.camera.depth_im.dtype, self.camera.depth_im.shape))
        # obs['servo_1'] = self.servos.get(['servo_1'])
        obs['servo_2'] = self.servos.get(['servo_2'])
        obs['servo_3'] = self.servos.get(['servo_3'])
        return obs

    def step(self, action):
        pdb.set_trace()
        self.servos.set({'servo_2': action[0]})
        obs_dict = self._get_obs()
        return obs_dict['depth_image'], self.get_reward(), self.is_done(), {}

    def get_reward(self):
        # pos = self.servos.get(['servo_1', 'servo_2', 'servo_3'])
        pos = self.servos.get(['servo_2', 'servo_3'])
        reward = -abs(pos[0] - pos[1])
        return reward

    def is_done(self):
        return False

    def reset(self):
        self.reset_pose = {
            # 'servo_1': np.random.uniform(low=-1.0, high=1.0),
            'servo_2': np.random.uniform(low=-1.0, high=1.0),
            'servo_3': np.random.uniform(low=-1.0, high=1.0),
        }
        self.servos.set(self.reset_pose)
        return self._get_obs()


if __name__ == '__main__':
    logging.getLogger(__name__).setLevel(logging.DEBUG)
    testcampo = CampoEnv()
    testcampo._get_obs()
    testcampo.reset()
    testcampo.step([-1.0])
