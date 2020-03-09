import numpy as np
from Game.ScapeGame import *
from time import sleep
import copy
from sys import exit
import numpy as np

import torch.nn as nn

import torch.nn.functional as F
import torch

TOT_ACTIONS = 5
EPISODE_DURATION = 1000
TEST_TIME = 100
SUCCESS_SEUIL = 50
VERBOSE = True
SCORE = 25


def act_policy(s, net):
    g = net(s)
    h = g.detach().numpy()
    cumsum_a = np.cumsum(h)

    #print(cumsum_a)
    #print(np.where(np.random.rand() < cumsum_a))
    
    try:
        return np.where(np.random.rand() < cumsum_a)[0][0]
    except:
        return 0
    #return h.argmax()


def test_policy(env, net, num_episodes = TEST_TIME , max_episode_length=EPISODE_DURATION, render= False):

    num_success = 0
    num_fired = 0
    num_out_range = 0
    average_return = 0
    l = 0

    for i_episode in range(num_episodes):
        _, _, episode_rewards, info = gen_rollout(env, net, max_episode_length, render)

        total_rewards = sum(episode_rewards)
        l+= len(episode_rewards)

        if info == "success":
            num_success+=1

        if info == "fired":
            num_fired+=1

        if info == "out of range":
            num_out_range+=1

        average_return += (1.0 / num_episodes) * total_rewards


    if num_success > SUCCESS_SEUIL:
        success = True
    else:
        success = False

    return success, (1.0 / num_episodes) * num_success, (1.0 / num_episodes) * num_fired, (1.0 / num_episodes) * num_out_range, average_return,  (1.0 / num_episodes) * l

def train(env, net, max_episode_length = EPISODE_DURATION, render = False):

    #lr = 0.1
    #optimizer = torch.optim.SGD(net.parameters(), lr=lr, momentum=0.0)

    avg_max_success = 0

    i_episode = 0
    average_returns = []
    average_success = []
    average_out = []
    average_fired = [] 
    average_par = []

    success = False
    
    success, avg_s, avg_fired, avg_out, R, l = test_policy(env, net)
    average_returns.append(R)
    average_success.append(avg_s)
    average_out.append(avg_out)
    average_fired.append(avg_fired)
    average_par.append(l)

    # Train until success
    while (not success):

        episode_states, episode_actions, episode_rewards, info = gen_rollout(env, net, max_episode_length, render)
        #print(len(episode_rewards))

        #net.get_weights()

        loss =0
      
        for t in range(len(episode_rewards)):
            R_t = sum(episode_rewards[t::])
            d =  net(episode_states[t])
            #print(g-d)
            #print(R_t,episode_states[t],d)
            loss -= R_t*d[episode_actions[t]]
            

        
        #optimizer.zero_grad()
        loss.backward()
        #optimizer.step()

        #net.get_weights()
        
        success, avg_s, avg_fired, avg_out, R, l = test_policy(env, net)
        average_returns.append(R)
        average_success.append(avg_s)
        average_out.append(avg_out)
        average_fired.append(avg_fired)
        average_par.append(l)

        i_episode += 1

        #if(i_episode==5): break
        if VERBOSE:
            print("Episode %d, average succes: %.2f, average fired: %.2f , average_out: %.2f, average_return: %.2f, average_len: %.2f" %(i_episode, avg_s, avg_fired, avg_out, R, l))

        if(avg_s > avg_max_success):
            avg_max_success = avg_s
            print("Max success rate excedeed")

    return i_episode, average_success, average_fired, average_out, average_returns, average_par

# Generate an episode
def gen_rollout(env, net, max_episode_length=EPISODE_DURATION, render=False):

    s_t = env.reset()
    episode_states = []
    episode_actions = []
    episode_rewards = []
    episode_states.append(s_t)
    success = False

    for t in range(max_episode_length):

        if render:
            env.render()
        a_t = act_policy(s_t, net)
        s_t, r_t, done, info = env.gameloop(a_t)
    
        episode_states.append(s_t)
        episode_actions.append(a_t)
        episode_rewards.append(r_t)
        if done:
            break
        if(t==(max_episode_length-1)):
            print("ops")


        
    return episode_states, episode_actions, episode_rewards, info



class net(nn.Module):
    def __init__(self, init):
        super(net, self).__init__()
        self.ln1 = nn.Linear(3,4, bias=False)
        #self.ln1.weights = torch.as_tensor(init)
        #self.ln2 = nn.Linear(15,5, bias=True)
        self.nett =  nn.Sequential(
            self.ln1, 
            nn.Softmax(dim=0)
        )

    def forward(self, s):
        d = list(s)
        #print(self.nett(torch.Tensor(d)))
        return torch.log(self.nett(torch.Tensor(d)))

    def get_weights(self):
        print("Actual weights")
        print(self.ln1.weight)
        #print(self.ln2.weight)


def main():
    space_dim = 3
    np.random.seed(719090)
    W_init = np.load("./../W_train28.npy")
    #print(W_init)

    Net = net(W_init)
    #d =Net( (9,3,4))
    #Net.get_weights()
    

    env = ScapeGame(grid_size=(15,15), show_mines=False, nlives=20, speed=20)

    #Net.get_weights()
    # Train agent
    i_episode, average_success, average_fired, average_out, average_returns, average_par = train(env, Net, render= False)

    #Net.get_weights()

    #a = test_policy(env, W_init, num_episodes = 20 , max_episode_length=EPISODE_DURATION, render= True)
    #print(a)


if __name__ == '__main__': 
    main()