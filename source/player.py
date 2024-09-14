import pygame
from settings import *


class Player(pygame.sprite.Sprite):
    def __init__(self, pos, groups):
        super().__init__(groups)
        # SETUP.
        self.image = pygame.Surface((32, 64))
        self.image.fill("green")
        self.rect = self.image.get_frect(center=pos)
        # MOVEMENT.
        self.direction, self.speed = Vector2(), 200

    def input(self):
        keys = pygame.key.get_pressed()
        # HORIZONTAL MOVEMENT.
        if keys[pygame.K_LEFT]:
            self.direction.x = -1
        elif keys[pygame.K_RIGHT]:
            self.direction.x = 1
        else:
            self.direction.x = 0
        # VERTICAL MOVEMENT.
        if keys[pygame.K_UP]:
            self.direction.y = -1
        elif keys[pygame.K_DOWN]:
            self.direction.y = 1
        else:
            self.direction.y = 0
        # NORMALIZE MOVEMENT.
        if self.direction:
            self.direction = self.direction.normalize()

    def move(self, dt):
        # HORIZONTAL MOVEMENT.
        self.rect.centerx += self.direction.x * self.speed * dt
        # VERTICAL MOVEMENT.
        self.rect.centery += self.direction.y * self.speed * dt

    def update(self, dt):
        self.input()
        self.move(dt)
