import gym
from gym import spaces, error
from gym.utils import seeding

import pygame, math, random
from pygame.locals import *
import argparse


NUM_ACTIONS = 5
'''
0 -> left
1 -> right
2 -> up
3 -> down
4 -> do nothing
'''

class Alien(pygame.sprite.Sprite):
    """  Alien class - inherits from pygame Sprite class - all the aliens on the screen"""
    def __init__(self, position, side=1,blocksize=40, topscreen = 580, speed=1):
        pygame.sprite.Sprite.__init__(self)
        self.imagearray=[]
        self.images = pygame.image.load('light.bmp').convert()
        self.images.set_colorkey((255,0,255))
        for i in range(0,120,24):
            self.imagearray.append(pygame.transform.scale(self.images.subsurface((i,0,24,24)),(blocksize,blocksize)))
        self.image = self.imagearray[0]
        self.rect = self.imagearray[0].get_rect()
        self.blocksize= blocksize
        self.side = side
        self.position=position
        self.topscreen = topscreen
        self.speed = speed

        self.reset()

        self.movement_ticks = 0
        self.animationcounter = random.randrange(0,4)
        self.animation_ticks = 0

    def update(self,timer,d):
        if self.movement_ticks < timer:
            self.movment_ticks = timer
            if self.rect.left < 0 or self.rect.left > self.topscreen:
                self.direction[0] = -self.direction[0]
            if self.rect.top < 0 or self.rect.top > self.topscreen:
                self.direction[1] = -self.direction[1]

            if(self.side==1):
                self.rect.top = d*self.blocksize
            else:
                self.rect.top = self.topscreen- d*self.blocksize

            self.movement_ticks += 10

            self.image = self.imagearray[self.animationcounter]
            if self.animation_ticks < timer:
                self.animation_ticks = timer
                self.animationcounter -= 1
                if self.animationcounter < 0:
                    self.animationcounter = 4
                self.animation_ticks += 150

    def get_grid_coord(self):
        return (int(self.rect.top/self.blocksize)+1)

    def reset(self):
        if(self.side==1):
            self.rect.topleft = [self.position*self.blocksize,0]
            self.direction = [0,self.speed*self.blocksize]
        else:
            self.rect.topleft = [self.position*self.blocksize,self.topscreen]
            self.direction = [0,-self.speed*self.blocksize]



class BaseShip(pygame.sprite.Sprite):
    """ the BaseShip class """
    def __init__(self, topscreen, topwidth, blocksize):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.transform.scale(pygame.image.load('baseship.bmp').convert(), (blocksize, blocksize))
        self.image.set_colorkey((255,0,255))
        self.rect = self.image.get_rect()
        self.topscreen = topscreen
        self.topwidth = topwidth
        self.rect.topleft = [0,self.topscreen]
        self.blocksize= blocksize

    def update(self,x,y):
        self.rect.left = x*self.blocksize
        self.rect.top = y*self.blocksize

    def get_grid_coord(self):
        return (int(self.rect.left/self.blocksize), int(self.rect.top/self.blocksize))

    def reset(self):
        self.rect.topleft = [0,self.topscreen]


class End(pygame.sprite.Sprite):
    """ the Missile class """
    def __init__(self, initialposition, blocksize):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.transform.scale(pygame.image.load('quadrado-vermelho.png').convert(), (blocksize,blocksize))
        self.rect = self.image.get_rect()
        self.rect.topleft = initialposition

    def update(self):
        pass

class Mine(pygame.sprite.Sprite):
    """ the Missile class """
    def __init__(self, initialposition, blocksize):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.transform.scale(pygame.image.load('mine.bmp').convert(), (blocksize,blocksize))
        self.rect = self.image.get_rect()
        self.rect.topleft = initialposition

    def update(self):
        pass

class Explosion(pygame.sprite.Sprite):
    """  Explosion class - the explosions on screen obviously """
    def __init__(self, initialposition):
        pygame.sprite.Sprite.__init__(self)
        self.imagearray=[]
        self.images = pygame.image.load('explosion.bmp').convert()
        self.images.set_colorkey((255,0,255))
        for i in range(0,240,60):
            self.imagearray.append(self.images.subsurface((i,0,60,60)))
        self.image = self.imagearray[0]
        self.rect = self.imagearray[0].get_rect()
        self.animation_ticks = 0
        self.animationcounter = 0
        self.rect.topleft = initialposition

    def update(self,timer):
        if self.animation_ticks < timer:
            self.animation_ticks = timer
            self.image = self.imagearray[self.animationcounter]
            self.animationcounter += 1
            if self.animationcounter > 3: self.kill()
            self.animation_ticks += 50


# Make game compatible with gym enviroment
class ScapeGame(gym.Env):

    # if interactive i set to True, step function is ignored and the user plays with the game  
    def __init__(self, grid_size= (10,10), step = 1, speed= 15, free_play= True, blocksize=45):
        super().__init__()
        self.action_space = spaces.Discrete(5)
        self.grid_size=grid_size
        self.observation_space = (spaces.Discrete(self.grid_size[0]), spaces.Discrete(self.grid_size[1]), spaces.Discrete(1+self.grid_size[1]))
        self.grid_size= grid_size
        self.speed = speed
        self.block_size= blocksize
        self.gameover =0
        self.grid_size=grid_size
        self.step = step
        self.free_play= free_play
        self.winsize= [(grid_size[0]+1)*self.block_size, (grid_size[1])*self.block_size]
        self.gui_starter = False
        self.mine_cells = self.get_mine_cells()
        self.decreasing = True
        

    def set_free_play(self,d):
        self.free_play = d

    def ghost_state_to_cells(self, d):
        ghost_cells = []
        if(d==0 or d==self.grid_size[1]): return ghost_cells
        else:
            # (ghost_y odd + ghost_y pair == self.grid_size[1])
            f = self.grid_size[1]-d
    
            #upper cells: 
            for i in range(0, (self.grid_size[0]+1),2):
                ghost_cells.append((i, d))

            #lower cells
            for i in range(1, (self.grid_size[0]+1),2):
                ghost_cells.append((i, f))

            return ghost_cells
    
    def get_mine_cells(self):
        mine_cells= []
        f = self.grid_size[0]

        for i in range(0,f+1,2):   
            mine_cells.append((i, math.floor(self.grid_size[1]/4)))    
            mine_cells.append((i, self.grid_size[1]-math.ceil(self.grid_size[1]/4)))

        for i in range(1,f,2):  
            mine_cells.append((i, math.floor(self.grid_size[1]/2)))           

        return mine_cells


    def gameloop(self, direction):  
        nextpositionx, nextpositiony = self.observation[0], self.observation[1]
        nextd = self.observation[2]

        if(self.observation[2]==0 or self.observation[2]==(self.grid_size[1]-1)):
            if(self.decreasing==True): 
                self.decreasing= False
            else: 
                self.decreasing= True

        if(self.decreasing==True): 
            nextd= self.observation[2]-1
        else:
            nextd= self.observation[2]+1

        if(direction==0):
            nextpositionx-=1
        if(direction==1):
           nextpositionx+=1
        if(direction==2):
            nextpositiony-=1
        if(direction==3):
            nextpositiony+=1


        self.observation = nextpositionx, nextpositiony , nextd

        if(nextpositiony==0 and nextpositionx==(self.grid_size[0])):
            if(self.free_play==False): 
                self.reset()
            return self.observation, 1, True, {"success"}

        if(nextpositionx<0 or nextpositionx> (self.grid_size[0])):
            self.reset()
            return self.observation, 0, True, {"out of range"}

        if(nextpositiony<0 or nextpositiony> (self.grid_size[1]-1)):
            self.reset()
            return self.observation, 0, True, {"out of range"}

        if((nextpositionx,nextpositiony) in self.ghost_state_to_cells(self.alien_example_instance[0].get_grid_coord())):
            if(self.free_play==False): 
                self.reset()
            
            return self.observation, 0, True, {"fired"}
            
        if((nextpositionx,nextpositiony) in self.mine_cells):
            # if the bomb is fired
            if(random.random()> 1/2):
                if(self.free_play==False): 
                    self.reset()
                return self.observation, 0, True, {"step_bomb"}
            else:
                return self.observation, 0, False, {"step_bomb"}
            

        return self.observation, 0, False, {}

    def step(self, action):
        return self.observation_space, 0, True, {}

    def reset(self):
        self.observation = (0,self.grid_size[1]-1, self.grid_size[1]-2)
        return self.observation

    def game_gui_init(self):
        self.clock = pygame.time.Clock()
        self.screen = pygame.display.set_mode(self.winsize)

        self.aliens = pygame.sprite.RenderUpdates()
        self.mines = pygame.sprite.RenderUpdates()

        ### lets create all the alien objects
        j = self.grid_size[0]
        self.alien_example_instance= []
        self.mines_instances = []

        for i in range(0,j+1):
            # get one ghost instance to calculate coordinates
            self.alien_example_instance.append(Alien(position=i, speed = self.step,side= i%2,blocksize= self.block_size, topscreen=self.winsize[1]-self.block_size))
            self.aliens.add(self.alien_example_instance[-1])
            if(i%2==1): 
                self.mines_instances.append(Mine([i*self.block_size, int(self.grid_size[1]/2)*self.block_size], self.block_size))
                self.mines.add(self.mines_instances[-1])
            else:
                self.mines_instances.append(Mine([i*self.block_size, math.floor(self.grid_size[1]/4)*self.block_size], self.block_size))
                self.mines.add(self.mines_instances[-1])
                self.mines_instances.append(Mine([i*self.block_size, self.winsize[1]-math.ceil(self.grid_size[1]/4)*self.block_size], self.block_size))
                self.mines.add(self.mines_instances[-1])


        self.baseship = pygame.sprite.RenderUpdates()
        self.ship_instance=BaseShip(self.winsize[1]-self.block_size, self.winsize[0]- self.block_size, self.block_size)
        self.baseship.add(self.ship_instance)

        self.end = pygame.sprite.RenderUpdates()
        self.end.add(End([self.winsize[0]-self.block_size, 0], self.block_size))

        self.missiles = pygame.sprite.RenderUpdates()

        self.explosions = pygame.sprite.RenderUpdates()

        self.background = pygame.transform.scale(pygame.image.load('background3.bmp').convert(), self.winsize)
        self.screen.blit(self.background,(0,0))

        
        pygame.init()

        pygame.mixer.pre_init(44000, 16, 2, 4096)
        self.missile = pygame.mixer.Sound('missile.wav')
        self.explosion = pygame.mixer.Sound('explosion.wav')
        self.basehit = pygame.mixer.Sound('basehit.wav')
        self.swarm = pygame.mixer.Sound('swarm.wav')
        self.swarm.play()
        
        pygame.display.update()


    def game_gui_render(self):
        time = pygame.time.get_ticks()

        self.end.clear(self.screen,self.background)
        self.mines.clear(self.screen,self.background)
        self.baseship.clear(self.screen,self.background)
        self.aliens.clear(self.screen,self.background)
        self.missiles.clear(self.screen,self.background)
        self.explosions.clear(self.screen,self.background)

        self.baseship.update(self.observation[0], self.observation[1])
        self.end.update()

        self.aliens.update(time, self.observation[2])
        self.mines.update()
        self.explosions.update(time)

        for i in pygame.sprite.groupcollide(self.baseship, self.aliens, False, False):
            a,b,c,d = i.rect
            self.explosions.add(Explosion((a,b)))
            self.basehit.play()

        for i in pygame.sprite.groupcollide(self.baseship, self.mines, False, False):
            a,b,c,d = i.rect
            self.explosions.add(Explosion((a,b)))
            self.basehit.play()

        rectlistend = self.end.draw(self.screen)
        rectlistmines= self.mines.draw(self.screen)
        rectlistbaseship = self.baseship.draw(self.screen)
        rectlistaliens = self.aliens.draw(self.screen)        

        rectlistexplosions = self.explosions.draw(self.screen)
        pygame.display.update(rectlistend)
        pygame.display.update(rectlistmines)
        pygame.display.update(rectlistbaseship)
        pygame.display.update(rectlistaliens)
        pygame.display.update(rectlistexplosions)
        
        self.clock.tick(self.speed)

    def render(self):
        if(self.gui_starter==False):
            self.game_gui_init()
            self.gui_starter=True
            self.game_gui_render()
        else:
            self.game_gui_render()


def parse_args():
    parser = argparse.ArgumentParser(description='')
    parser.add_argument('--h', default=15, type=int)
    parser.add_argument('--w', default=18, type=int)
    parser.add_argument('--step', default=1.0, type=int)
    parser.add_argument('--speed', default=18, type=int)
    parser.add_argument('--block_size', default=40, type=int)
    parser.add_argument('--free_play', default=True, type=bool)
    parser.add_argument('--gameplay', default=0, type=int)

    args = parser.parse_args()
    return args
    
if __name__ == '__main__': 
    args = parse_args()
    env = ScapeGame(grid_size=(args.w,args.h), speed = args.speed, free_play= args.free_play, step= args.step, blocksize= args.block_size)

    env.set_free_play(True)
   
    print(env.action_space)
    print(env.observation_space)

    done = False
    env.reset()

    interactive = True
    while True:
        
        direction = 4
        if(args.gameplay!=0):
            #replace by some policy
            pass
        else:
            if(interactive==True):
                # the below code throws a exception when pygame tries to get event and the display is not initialized
                try:
                    for event in pygame.event.get():
                        if event.type == QUIT:
                            exit()

                    pressed_keys = pygame.key.get_pressed()

                    if pressed_keys[K_LEFT]: direction = 0
                    if pressed_keys[K_RIGHT]: direction = 1
                    if pressed_keys[K_UP]: direction = 2
                    if pressed_keys[K_DOWN]: direction = 3
        
                except: 
                    pass

        env.render()
        observation, reward, done, info = env.gameloop(direction)
        print(observation, reward,done,info)
        



    