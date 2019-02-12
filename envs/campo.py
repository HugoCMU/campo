"""Gym environment for campo RL algo."""
import collections
import logging
import os
import gym
import time

# Manually import realsense module
import importlib.util

import pdb

REALSENSE_PATH = os.path.abspath(
    os.path.join(os.path.dirname(os.path.abspath(__file__)), '../../realsense-tcp-module/cameras.py'))
spec = importlib.util.spec_from_file_location("realsense-tcp-module.cameras", REALSENSE_PATH)
realsense_module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(realsense_module)


class CampoEnv(gym.Env):
    """Gym environment for campo."""

    def __init__(self):
        super().__init__()
        self.camera = realsense_module.RealSense(tcp_ip='127.0.0.1', tcp_port=50200)
        time.sleep(1)  # Give camera some time to load data

    def _get_obs(self):
        obs = collections.OrderedDict()
        # Fetch latest information from camera
        obs['color_image'] = self.camera.color_im
        obs['depth_image'] = self.camera.depth_im
        obs['timestamp'] = self.camera.timestamp
        obs['color_intrinsics'] = self.camera.color_intr
        obs['depth_intrinsics'] = self.camera.depth_intr
        obs['depth2color_extrinsic'] = self.camera.depth2color_extr
        pdb.set_trace()
        logging.debug('STEP')
        logging.debug('timestamp %s' % self.camera.timestamp)
        logging.debug('color image   %s   %s' % (self.camera.color_im.dtype, self.camera.color_im.shape))
        logging.debug('depth image   %s   %s' % (self.camera.depth_im.dtype, self.camera.depth_im.shape))
        return obs

    def step(self, action):
        del action
        is_done = False
        obs = self._get_obs()
        reward = 1.0
        pdb.set_trace()
        return obs, reward, is_done, {}

    def reset(self):
        return self._get_obs()


if __name__ == '__main__':
    logging.getLogger(__name__).setLevel(logging.DEBUG)
    pdb.set_trace()
    testcampo = CampoEnv()
    testcampo._get_obs()
    testcampo.reset()
    testcampo.step(None)
