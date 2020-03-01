#  Solving a handcrafted scape game environment using Reinforcement Learning

Reinforcement Learning project using AIGym library /envs


# Game Rules and Goal

![Ghost Movements and Game Goal](./images/popo3.gif)
![Ship Movements](./images/popo.gif)


### Quick setut 

#### Dependencies 
 
 - pygame
 - gym
 - math
 - random
 - argparse

### Some parameters:

 - **--h** (*default=15, type=int*)                     => height of grid        
 - **--w** (*default=18, type=int*)                     => width of grid
 - **--step** (*default=1.0, type=int*)                 => The step given by the ghost per time step, mesure in grid cells
 - **--speed** (*default=18, type=int*)                 => Renderind speed (affects only human players)
 - **--block_size** (*default=40, type=int* )           => Control the pixel size of a grid squared cell 
 - **--free_play** (*default=False, type=bool*)         => Game don't restart automatically when ship is hit 