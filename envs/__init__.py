from gym.envs.registration import register

register(
    id='campo-v0',
    entry_point='campo.envs:CampoEnv',
    max_steps=10,
)