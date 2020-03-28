# -*- coding: utf-8 -*-
# ref: https://gym.openai.com/evaluations/eval_1lfzNKEHS9GA7nNWE73w
from ScapeGame import ScapeGame
import numpy as np
import gym
import time


env = ScapeGame(grid_size=(8,8), nlives=2, random_init=True, show_mines=False)
env.set_free_play(True)
turn_limit = 100
is_monitor = True

def q_learning():
	oS = env.observation_space
	aS = env.action_space
	q_values = np.zeros((int(oS.high[0]), int(oS.high[1]), int(oS.high[2]), aS.n))
	# print((int(oS.high[0]), int(oS.high[1]), int(oS.high[2]), aS.n))
	# print((oS[0].n, oS[1].n, oS[2].n, aS.n))
	learn_count = 100000
	alpha = 0.1 # learning rate
	gamma = 0.99 # reward discount
	turn_limit = 100
	for i in range(learn_count):
		# one episode learning
		state = env.reset()
		#env.render()

		for t in range(turn_limit):
			# print(state, end=" ")
			action = env.action_space.sample() # random
			next_state, reward, done, info = env.step(action)
			#self.env.render()
			q_next_max = np.max(q_values[tuple(next_state)])
			q_values[tuple(state)][action] = (1 - alpha) * q_values[tuple(state)][action] + alpha * (reward + gamma * q_next_max)
			state = next_state
			if done:
				break
		# print("")
	return q_values


def run():
	state = env.reset()
	for t in range(turn_limit):
		act = np.argmax(q_values[tuple(state)])
		state, reward, done, info = env.step(act)
		if done:
			return 1 * info["is_success"]
	return 0.0 # over limit

q_values = q_learning()
print(q_values)
n_trials = 100
mean_values = []
for j in range(100):
	successful_trials = 0
	for i in range(n_trials):
		successful_trials += run()
	mean_values.append(successful_trials / n_trials)
	# print(successful_trials / n_trials)
mean = sum(mean_values) / len(mean_values)
var = sum([(x - mean)**2 for x in mean_values]) / len(mean_values)
print("&", "{:.2f}".format(100 * mean), "\\% ", end="")
print("&", "{:.2f}".format(10000 * var), "\\% ", end="")
print("&", "{:.2f}".format(100 * max(mean_values)), "\\% \\\\")
env.close()
