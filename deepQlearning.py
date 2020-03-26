import gym

import numpy as np
from Game.ScapeGame import *
from time import sleep
import copy
from sys import exit
import os


from stable_baselines.common.vec_env import DummyVecEnv
from stable_baselines.deepq.policies import MlpPolicy, LnMlpPolicy, CnnPolicy, LnCnnPolicy
from stable_baselines import DQN

SUCCESS_SEUIL = 50
EPISODE_DURATION = 500

TEST_TIME = 100


# Generate an episode
def gen_rollout(env, model, max_episode_length=EPISODE_DURATION, render=True):

    s_t = env.reset()
    episode_states = []
    episode_actions = []
    episode_rewards = []
    episode_states.append(s_t)
    success = False

    for t in range(max_episode_length):
        if render:
            env.render()
        a_t, _s = model.predict(s_t)
        s_t, r_t, done, info = env.step(a_t)
    
        episode_states.append(s_t)
        episode_actions.append(a_t)
        episode_rewards.append(r_t)
        if done:
            break
        if(t==(max_episode_length-1)):
            print("ops")

        
    return episode_states, episode_actions, episode_rewards, info


def test_policy(env, model, num_episodes = TEST_TIME , max_episode_length=EPISODE_DURATION, render= False):

    num_success = 0
    num_fired = 0
    num_out_range = 0
    average_return = 0
    l = 0

    for i_episode in range(num_episodes):
        _, _, episode_rewards, info = gen_rollout(env, model, max_episode_length, render)

        total_rewards = sum(episode_rewards)
        l+= len(episode_rewards)

        if info.get("is_success"):
            num_success+=1

        if info.get("fired"):
            num_fired+=1

        if info.get("out of range"):
            num_out_range+=1

        average_return += (1.0 / num_episodes) * total_rewards


    if num_success > SUCCESS_SEUIL:
        success = True
    else:
        success = False

    return success, (1.0 / num_episodes) * num_success, (1.0 / num_episodes) * num_fired, (1.0 / num_episodes) * num_out_range, average_return,  (1.0 / num_episodes) * l

'''
model = DQN(MlpPolicy, env, verbose=1)
model.learn(total_timesteps=25000)
model.save("deepq_cartpole")


env = gym.make('CartPole-v1')

model = DQN(MlpPolicy, env, verbose=1)
model.learn(total_timesteps=25000)
model.save("deepq_cartpole")

del model # remove to demonstrate saving and loading
'''


'''
obs = env.reset()
while True:
    action, _states = model.predict(obs)
    obs, rewards, dones, info = env.step(action)
    env.render()
'''


def callb(local,globa):
    last_epis = 0  
    
    if(len(local['episode_successes'])%100==1):
        if((local['num_episodes'])%100 ==2):
            if(last_epis!=(local['num_episodes'])):
                i_episode= (local['num_episodes']-2)
                if(not os.path.exists("deepq_scapegame_"+str(i_episode)+".zip")):
                    local['self'].save("deepq_scapegame_"+ str(i_episode))


def train(env, epochs, model=None):

    if(model==None):
        model = DQN(LnMlpPolicy, env, verbose=1)

    model.learn(total_timesteps=epochs, callback=callb)
        
        
def main():
    env = ScapeGame(grid_size=(8,8), show_mines=True, nlives=5, speed=20, random_init=True)

    '''
    model = DQN.load("deepq_scapegame_400")
    model.set_env(env)
    num_episodes = 10
    
    for i_episode in range(num_episodes):
        done = False
        obs = env.reset()
        env.render()
        while not done:
            action, _states = model.predict(obs)
            obs, rewards, dones, info = env.step(action)
            env.render()
    '''

    train(env,100000)
    
    
if __name__ == '__main__': 
    main()
