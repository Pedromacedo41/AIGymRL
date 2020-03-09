import numpy as np
from Game.ScapeGame import *
from time import sleep
import copy
from sys import exit

TOT_ACTIONS = 5
EPISODE_DURATION = 500
ALPHA_INIT = 10
TEST_TIME = 100
SUCCESS_SEUIL = 50
VERBOSE = True
SCORE = 25

def softmax(q):
     # rescale to avoid overflow problems: 
    if ((q.max()- q.min()) != 0 ):
        q = (q - q.min())/abs( q.max()- q.min())
    else:
        print("attention")

    factors = np.exp(q)
    return factors / np.sum(factors)

def get_policy(s, W):
    F = (W @ s)
    return softmax(F)

def act_policy(s, W):
    cumsum_a = np.cumsum(get_policy(s,W))
    #print(cumsum_a)
    return np.where(np.random.rand() < cumsum_a)[0][0]
   

def policy_grad(s, W,  action):
    s_v = np.array(s)
    pol_dis = get_policy(s_v,W)
    grad = np.stack([-s_v*pol_dis[i] for i in range(TOT_ACTIONS)], axis=0)
    grad[action,:] +=s_v
    return grad

def test_policy(env, W, num_episodes = TEST_TIME , max_episode_length=EPISODE_DURATION, render= False):

    num_success = 0
    num_fired = 0
    num_out_range = 0
    average_return = 0
    l = 0

    for i_episode in range(num_episodes):
        _, _, episode_rewards, info = gen_rollout(env, W, max_episode_length, render)

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

def train(env, w_init, max_episode_length = EPISODE_DURATION, alpha_init = ALPHA_INIT, render = False):

    W = copy.deepcopy(w_init)
    PG = np.zeros(shape=W.shape)


    avg_max_success = 0

    i_episode = 0
    average_returns = []
    average_success = []
    average_out = []
    average_fired = [] 
    average_par = []

    success = False
    
    success, avg_s, avg_fired, avg_out, R, l = test_policy(env, W)
    average_returns.append(R)
    average_success.append(avg_s)
    average_out.append(avg_out)
    average_fired.append(avg_fired)
    average_par.append(l)
    
    alpha = alpha_init

    # Train until success
    while (not success):

        # Rollout
        episode_states, episode_actions, episode_rewards, info = gen_rollout(env, W, max_episode_length, render)
        #print(len(episode_rewards))
        
        # Schedule step size
        #alpha = alpha_init
        PG[:,:] = 0
        #alpha = alpha_init / (1 + i_episode)

        # Compute gradient
        for t in range(len(episode_rewards)):
            R_t = sum(episode_rewards[t::])
            #print(R_t)
            d = policy_grad(episode_states[t], W, episode_actions[t])
            #print(episode_actions[t])
            #print(episode_states[t])
            #print(d)
            #print(d)
            PG += d*R_t

        #break

        # Do gradient ascent
        #print(alpha)
        #print(PG)
        #print(W)
        np.add(alpha*PG, W, out= W)
        #W+=alpha*PG
        #print(PG)
       
        #print(alpha)
        #print(PG)
        #print("W")
        #print(W)       
        
        success, avg_s, avg_fired, avg_out, R, l = test_policy(env, W)
        average_returns.append(R)
        average_success.append(avg_s)
        average_out.append(avg_out)
        average_fired.append(avg_fired)
        average_par.append(l)
        
        
        i_episode += 1

        if VERBOSE:
            print("Episode %d, average succes: %.2f, average fired: %.2f , average_out: %.2f, average_return: %.2f, average_len: %.2f" %(i_episode, avg_s, avg_fired, avg_out, R, l))

        if(avg_s > avg_max_success):
            avg_max_success = avg_s
            print("Max success rate excedeed")
            np.save("./../W_train.npy", W)
            alpha = alpha*0.5

    return W, i_episode, average_success, average_fired, average_out, average_returns, average_par

# Generate an episode
def gen_rollout(env, W, max_episode_length=EPISODE_DURATION, render=False):

    s_t = env.reset()
    episode_states = []
    episode_actions = []
    episode_rewards = []
    episode_states.append(s_t)
    success = False

    for t in range(max_episode_length):

        if render:
            env.render()
        a_t = act_policy(s_t, W)
        s_t, r_t, done, info = env.gameloop(a_t)
    
        episode_states.append(s_t)
        episode_actions.append(a_t)
        episode_rewards.append(r_t)
        if done:
            break
        if(t==(max_episode_length-1)):
            print("ops")


        
    return episode_states, episode_actions, episode_rewards, info



def main():
    space_dim = 3
    np.random.seed(7)

    try: 
        # pre-trained matrix
        W_init = np.load("./../W_train28.npy")
        print("W initilized from pre-training")
    except:
        W_init = np.random.randn(TOT_ACTIONS,space_dim)

    #s_init = np.random.randn(space_dim)

    #print(act_policy(s_init,W_init))


    '''
    print(s_init)
    print(s_init.shape)
    print(policy_grad(s_init,W_init, 2))
    print(policy_grad(s_init,W_init, 2).shape)
    '''

    env = ScapeGame(grid_size=(15,15), show_mines=False, nlives=20, speed=20)

    # Train agent
    W, i_episode, average_success, average_fired, average_out, average_returns, average_par = train(env, W_init, render= False)

    #a = test_policy(env, W_init, num_episodes = 20 , max_episode_length=EPISODE_DURATION, render= True)
    #print(a)


if __name__ == '__main__': 
    main()