import collections
import os
import gym
import time

# Manually import realsense module
import importlib.util

REALSENSE_PATH = os.path.abspath(
    os.path.join(os.path.dirname(os.path.abspath(__file__)), '../../realsense-tcp-module/cameras.py'))
spec = importlib.util.spec_from_file_location("realsense-tcp-module.cameras", REALSENSE_PATH)
realsense_module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(realsense_module)


class CampoEnv(gym.Env):
    """Gym environment for campo."""

    def __init__(self):
        # super().__init__()
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

    def step(self, action):
        pass

    def reset(self):
        pass

    def render(self, mode='human', close=False):
        pass


if __name__ == '__main__':
    testcampo = CampoEnv()
    testcampo._get_obs()
