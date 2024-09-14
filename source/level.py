import pygame
from settings import *


class Level:
    def __init__(self):
        self.screen = pygame.display.get_surface()
        # GROUPS.
        self.all_sprites = pygame.sprite.Group()

    def run(self, dt):
        self.all_sprites.update()
        self.all_sprites.draw(self.screen)
