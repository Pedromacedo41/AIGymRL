import numpy as np
from Game.ScapeGame import *
from time import sleep
import copy

from sys import exit


import gym

from stable_baselines.common.vec_env import DummyVecEnv
from stable_baselines.deepq.policies import MlpPolicy
from stable_baselines import DQN


def main():
    print("a")
    #env = ScapeGame(grid_size=(15,15), show_mines=False, nlives=20, speed=20)
    model = DQN(MlpPolicy, env, verbose=1)
    model.learn(total_timesteps=25000)
    model.save("./deepq_cartpole")

    #del model # remove to demonstrate saving and loading

    '''
    model = DQN.load("deepq_cartpole")

    obs = env.reset()
    while True:
        action, _states = model.predict(obs)
        obs, rewards, dones, info = env.step(action)
        env.render()
    '''

if __name__ == '__main__': 
    main()