import pygame
from settings import *
from player import Player


class Level:
    def __init__(self):
        self.screen = pygame.display.get_surface()
        # GROUPS.
        self.all_sprites = pygame.sprite.Group()
        # SETUP.
        self.load_data()

    def load_data(self):
        self.player = Player((640, 360), self.all_sprites)

    def run(self, dt):
        self.all_sprites.update(dt)
        self.all_sprites.draw(self.screen)
