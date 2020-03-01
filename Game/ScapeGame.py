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
class StatusDisplay(pygame.sprite.Sprite):
    """ this class is used to display the score etc at the top of the screen"""
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.font = pygame.font.SysFont("arial", 24)
        self.text = ""
        self.image = self.font.render(self.text, 1, (0, 0, 255))
        self.rect = self.image.get_rect()

    def update(self,text):
        self.text = text
        self.image = self.font.render(self.text, 1, (0, 0, 255))
        self.rect = self.image.get_rect()


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

        if(side==1):
            self.rect.topleft = [position*blocksize,0]
            self.direction = [0,speed*blocksize]
        else:
            self.rect.topleft = [position*blocksize,topscreen]
            self.direction = [0,-speed*blocksize]
        self.movement_ticks = 0
        self.animationcounter = random.randrange(0,4)
        self.animation_ticks = 0
        self.topscreen = topscreen

    def update(self,timer):
        if self.movement_ticks < timer:
            self.movment_ticks = timer
            if self.rect.left < 0 or self.rect.left > self.topscreen:
                self.direction[0] = -self.direction[0]
            if self.rect.top < 0 or self.rect.top > self.topscreen:
                self.direction[1] = -self.direction[1]

            self.rect.left = self.rect.left + self.direction[0]
            self.rect.top = self.rect.top + self.direction[1]

            self.movement_ticks += 10

            self.image = self.imagearray[self.animationcounter]
            if self.animation_ticks < timer:
                self.animation_ticks = timer
                self.animationcounter -= 1
                if self.animationcounter < 0:
                    self.animationcounter = 4
                self.animation_ticks += 150


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

    def update(self,direction):
        if direction == 0 and self.rect.left > 0:
            self.rect.left -= self.blocksize
        if direction == 1 and self.rect.left < self.topwidth:
            self.rect.left += self.blocksize
        if direction == 2 and self.rect.top > 0:
            self.rect.top -= self.blocksize
        if direction == 3 and self.rect.top < (self.topscreen):
            self.rect.top += self.blocksize


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
class ScapeGame():

    # if interactive i set to True, step function is ignored and the user plays with the game  
    def __init__(self, grid_size= (10,10), step = 1, speed= 15, free_play= True, interactive = False, blocksize=45):
        super().__init__()
        self.action_space = spaces.MultiDiscrete([1] * NUM_ACTIONS)
        self.observation_space = spaces.Box(low=0, high=300, shape=(2,))
        self.grid_size= grid_size
        self.speed = speed
        self.block_size= blocksize
        self.gameover =0
        self.grid_size=grid_size
        self.step = step
        self.winsize= [(grid_size[0]+1)*self.block_size, (grid_size[1])*self.block_size]

        pygame.init()

        pygame.mixer.pre_init(44000, 16, 2, 4096)
        self.missile = pygame.mixer.Sound('missile.wav')
        self.explosion = pygame.mixer.Sound('explosion.wav')
        self.basehit = pygame.mixer.Sound('basehit.wav')
        self.swarm = pygame.mixer.Sound('swarm.wav')

        self.clock = pygame.time.Clock()
        self.screen = pygame.display.set_mode(self.winsize)

        self.aliens = pygame.sprite.RenderUpdates()
        self.mines = pygame.sprite.RenderUpdates()

        ### lets create all the alien objects
        i = self.grid_size[0]
        while i >= 0:
            self.aliens.add(Alien(position=i, speed = self.step,side= i%2,blocksize= self.block_size, topscreen=self.winsize[1]-self.block_size))
            if(i%2==1): 
                self.mines.add(Mine([i*self.block_size, int(self.grid_size[1]/2)*self.block_size], self.block_size))
            else:
                self.mines.add(Mine([i*self.block_size, math.floor(self.grid_size[1]/4)*self.block_size], self.block_size))
                self.mines.add(Mine([i*self.block_size, self.winsize[1]-math.ceil(self.grid_size[1]/4)*self.block_size], self.block_size))

            i -= 1

        self.baseship = pygame.sprite.RenderUpdates()
        self.baseship.add(BaseShip(self.winsize[1]-self.block_size, self.winsize[0]- self.block_size, self.block_size))

        self.end = pygame.sprite.RenderUpdates()
        self.end.add(End([self.winsize[0]-self.block_size, 0], self.block_size))

        self.missiles = pygame.sprite.RenderUpdates()

        self.explosions = pygame.sprite.RenderUpdates()


        self.background = pygame.transform.scale(pygame.image.load('background3.bmp').convert(), self.winsize)
        self.screen.blit(self.background,(0,0))
  
        self.swarm.play()
        
        pygame.display.update()



    def gameloop(self):        
        time = pygame.time.get_ticks()

        for event in pygame.event.get():
                if event.type == QUIT:
                    exit()

        pressed_keys = pygame.key.get_pressed()

        direction = 4
        if pressed_keys[K_LEFT]: direction = 0
        if pressed_keys[K_RIGHT]: direction = 1
        if pressed_keys[K_UP]: direction = 2
        if pressed_keys[K_DOWN]: direction = 3

        self.end.clear(self.screen,self.background)
        self.mines.clear(self.screen,self.background)
        self.baseship.clear(self.screen,self.background)
        self.aliens.clear(self.screen,self.background)
        self.missiles.clear(self.screen,self.background)
        self.explosions.clear(self.screen,self.background)

        self.baseship.update(direction)
        self.end.update()

        self.aliens.update(time)
        self.mines.update()
        self.explosions.update(time)


        for i in pygame.sprite.groupcollide(self.baseship, self.aliens, False, False):
            a,b,c,d = i.rect
            self.explosions.add(Explosion((a,b)))
            self.gameover =1
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

    def step(self, action):
        return self.observation_space, 0, True, {}

    def reset(self):
        return self.observation_space

    def render(self):
        print("nothing")

    def restart(self):
        print("nothing")


def parse_args():
    parser = argparse.ArgumentParser(description='')
    parser.add_argument('--h', default=15, type=int)
    parser.add_argument('--w', default=18, type=int)
    parser.add_argument('--step', default=1.0, type=int)
    parser.add_argument('--speed', default=18, type=int)
    parser.add_argument('--block_size', default=40, type=int)
    parser.add_argument('--free_play', default=False, type=bool)

    args = parser.parse_args()
    return args
    
if __name__ == '__main__': 
    args = parse_args()
    env = ScapeGame(grid_size=(args.w,args.h), speed = args.speed, free_play= args.free_play, step= args.step, blocksize= args.block_size)

    while(True):
        env.gameloop()

    