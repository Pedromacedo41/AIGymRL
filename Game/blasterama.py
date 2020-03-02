#####################################################################
#
#
#   Blasterama.py
#
#   7th October 2008
#   rsbrooks@gmail.com
#
#   A no holes barred shootem up.  No rules, just shot as
#   many aliens as you can in wave after wave.  You have as
#   many lives / shields as you want.  Watch out for the initial
#   wave swarm, it's a killer !
#
#   left and right arrow to steer the ship, z key to fire.
#
#
#
#####################################################################

import pygame, math, random
from pygame.locals import *

### Some Globals

MAX_X = 500
MAX_XSHIP = 760
MAX_Y = 580
MIN_X = 0
MIN_Y = 0

##### change this value to get more aliens on the screen if you dare ( or if
##### your processor can take it !!!!
ALIENNUMBERS = 40

#### Class definitions


class StatusDisplay(pygame.sprite.Sprite):
	""" this class is used to display the score etc at the top of the screen"""
	def __init__(self):
		pygame.sprite.Sprite.__init__(self)
		self.lives = 0
		self.score = 0
		self.wave = 1
		self.font = pygame.font.SysFont("arial", 24)
		self.text = "SHIELD HITS: %d   MISSILE HITS: %d  WAVE NUMBER: %d" % (self.lives, self.score, self.wave)
		self.image = self.font.render(self.text, 1, (0, 0, 255))
		self.rect = self.image.get_rect()

	def update(self,lives,score,wave):
		if lives > 0:
			self.lives += 1
		elif score > 0:
			self.score += 1
		elif wave > 0:
			self.wave += 1
		self.text = "SHIELD HITS: %d   MISSILE HITS: %d  WAVE NUMBER: %d" % (self.lives, self.score, self.wave)
		self.image = self.font.render(self.text, 1, (0, 0, 255))
		self.rect = self.image.get_rect()





class Alien(pygame.sprite.Sprite):
	"""  Alien class - inherits from pygame Sprite class - all the aliens on the screen"""
	def __init__(self):
		pygame.sprite.Sprite.__init__(self)
		self.imagearray=[]
		self.images = pygame.image.load('light.bmp').convert()
		self.images.set_colorkey((255,0,255))
		for i in range(0,120,24):
			self.imagearray.append(pygame.transform.scale(self.images.subsurface((i,0,24,24)),(40,40)))
		self.image = self.imagearray[0]
		self.rect = self.imagearray[0].get_rect()
		self.rect.topleft = [random.randrange(0,780),random.randrange(0,580)]
		self.direction = [0,random.randint(-4,4)]
		if(self.direction[1]==0): self.direction[1]=4
		self.movement_ticks = 0
		self.animationcounter = random.randrange(0,4)
		self.animation_ticks = 0

	def update(self,timer):
		if self.movement_ticks < timer:
			self.movment_ticks = timer
			if self.rect.left < MIN_X or self.rect.left > MAX_X:
				self.direction[0] = -self.direction[0]
			if self.rect.top < MIN_Y or self.rect.top > MAX_Y:
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
	def __init__(self):
		pygame.sprite.Sprite.__init__(self)
		self.image = pygame.image.load('baseship.bmp').convert()
		self.image.set_colorkey((255,0,255))
		self.rect = self.image.get_rect()
		self.rect.topleft = [0,580]

	def update(self,direction):
		if direction == 0 and self.rect.left > MIN_X:
			self.rect.left -= 4
		if direction == 1 and self.rect.left < MAX_XSHIP:
			self.rect.left += 4
		if direction == 2 and self.rect.top > 0:
			self.rect.top -= 4
		if direction == 3 and self.rect.top < MAX_Y:
			self.rect.top += 4

class End(pygame.sprite.Sprite):
	""" the Missile class """
	def __init__(self, initialposition):
		pygame.sprite.Sprite.__init__(self)
		self.image = pygame.transform.scale(pygame.image.load('quadrado-vermelho.png').convert(), (80,25))
		self.rect = self.image.get_rect()
		self.rect.topleft = initialposition

	def update(self):
		pass


class Missile(pygame.sprite.Sprite):
	""" the Missile class """
	def __init__(self, initialposition):
		pygame.sprite.Sprite.__init__(self)
		self.image = pygame.image.load('missile.bmp').convert()
		self.image.set_colorkey((255,0,255))
		self.rect = self.image.get_rect()
		self.rect.topleft = initialposition

	def update(self):
		if self.rect.top > MIN_Y:
			self.rect.top -= 4
		else:
			self.kill()



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

class Sounds():
	""" play all the sounds in the game """
	def __init__(self):
		pygame.mixer.pre_init(44000, 16, 2, 4096)
		self.sounds = {"missile": pygame.mixer.Sound('missile.wav'),
		"explosion": pygame.mixer.Sound('explosion.wav'),
		"basehit": pygame.mixer.Sound('basehit.wav'),
		"swarm": pygame.mixer.Sound('swarm.wav')}

	def play(self, sound):
		if sound in self.sounds:
			self.sounds[sound].play()


def main():

	GAMEOVER = 0
	missile_missed = 0
	missile_hits = 0

	missileticks = 0

	WINSIZE = [800,600]
	pygame.init()

	pygame.mixer.pre_init(44000, 16, 2, 4096)
	sounds = Sounds()

	clock = pygame.time.Clock()
	screen = pygame.display.set_mode(WINSIZE)

	aliens = pygame.sprite.RenderUpdates()

	### lets create all the alien objects
	for i in range(ALIENNUMBERS):
		aliens.add(Alien())

	statusdisplay = pygame.sprite.RenderUpdates()
	statusdisplay.add(StatusDisplay())

	baseship = pygame.sprite.RenderUpdates()
	baseship.add(BaseShip())

	end = pygame.sprite.RenderUpdates()
	end.add(End([MAX_XSHIP, 0]))

	missiles = pygame.sprite.RenderUpdates()

	explosions = pygame.sprite.RenderUpdates()


	background = pygame.image.load('background3.bmp').convert()
	screen.blit(background,(0,0))



	pygame.display.update()

	sounds.play("swarm")


	GAMEOVER = 0
	while not GAMEOVER:

		time = pygame.time.get_ticks()
		print(time)

		direction = 4
		for event in pygame.event.get():
			if event.type == pygame.KEYDOWN:
				if event.key == pygame.K_LEFT:
					direction = 0
				if event.key == pygame.K_RIGHT:
					direction = 1
				if event.key == pygame.K_UP:
					direction = 2
				if event.key == pygame.K_DOWN:
					direction = 3
			if event.type == QUIT:
				exit()

		pressed_keys = pygame.key.get_pressed()

		if pressed_keys[K_LEFT]: direction = 0
		if pressed_keys[K_RIGHT]: direction = 1
		if pressed_keys[K_UP]: direction = 2
		if pressed_keys[K_DOWN]: direction = 3

		if pressed_keys[K_z]: fired = 1
		else: fired = 0


		baseship.clear(screen,background)
		aliens.clear(screen,background)
		missiles.clear(screen,background)
		explosions.clear(screen,background)
		statusdisplay.clear(screen,background)
		end.clear(screen,background)

		baseship.update(direction)
		missiles.update()
		end.update()

		aliens.update(time)
		explosions.update(time)



		for i in pygame.sprite.groupcollide(aliens, missiles, True, True):
			a,b,c,d = i.rect
			explosions.add(Explosion((a-20,b-20)))
			statusdisplay.update(0,1,0)
			sounds.play("explosion")

		for i in pygame.sprite.groupcollide(baseship, aliens, False, True):
			a,b,c,d = i.rect
			explosions.add(Explosion((a-20,b-20)))
			statusdisplay.update(1,0,0)
			sounds.play("basehit")

		rectlistend = end.draw(screen)
		rectlistbaseship = baseship.draw(screen)
		rectlistmissiles = missiles.draw(screen)
		rectlistaliens = aliens.draw(screen)

		if fired == 1 and time > missileticks:
			missileticks = time + 300
			a,b,c,d = rectlistbaseship[0]
			missiles.add(Missile((a+18,b)))
			sounds.play("missile")


		if len(rectlistaliens) == 0:
			for i in range(ALIENNUMBERS):
				aliens.add(Alien())
			statusdisplay.update(0,0,1)
			sounds.play("swarm")

		rectlistexplosions = explosions.draw(screen)
		rectliststatusdisplay = statusdisplay.draw(screen)
		pygame.display.update(rectlistend)
		pygame.display.update(rectlistbaseship)
		pygame.display.update(rectlistmissiles)
		pygame.display.update(rectlistaliens)
		pygame.display.update(rectlistexplosions)
		pygame.display.update(rectliststatusdisplay)



		clock.tick(150)



if __name__ == '__main__': main()
