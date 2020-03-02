# -*- coding: utf-8 -*-
# ref: https://gym.openai.com/evaluations/eval_1lfzNKEHS9GA7nNWE73w
from ScapeGame import ScapeGame
import numpy as np
import gym


env = ScapeGame()
env.set_free_play(True)
turn_limit = 100
is_monitor = True

def q_learning():
	oS = env.observation_space
	q_values = np.zeros((oS[0].n, oS[1].n, oS[2].n))
	learn_count = 10000
	for i in range(learn_count):
		alpha = 0.1 # learning rate
		gamma = 0.99 # reward discount
		# one episode learning
		state = env.reset()
		#self.env.render()
		turn_limit = 100

		for t in range(turn_limit):
			action = env.action_space.sample() # random
			next_state, reward, done, info = env.step(action)
			#self.env.render()
			q_next_max = np.max(q_values[next_state])
			q_values[state][action] = (1 - alpha) * q_values[state][action] + alpha * (reward + gamma * q_next_max)
			state = next_state
			if done:
				break
	return q_values


def run():
	state = env.reset()
	for t in range(turn_limit):
		act = np.argmax(q_values[state])
		state, reward, done, info = env.step(act)
		if done:
			return reward
	return 0.0 # over limit

q_values = q_learning()
successful_trials = 0
n_trials = 100
for i in range(n_trials):
	successful_trials += run()

print(successful_trials / n_trials)
env.close()
