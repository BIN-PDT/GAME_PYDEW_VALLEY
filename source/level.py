import pygame
from settings import *
from supports import import_image

from groups import AllSprites
from player import Player
from overlay import Overlay
from sprites import *


class Level:
    def __init__(self):
        self.screen = pygame.display.get_surface()
        # GROUPS.
        self.all_sprites = AllSprites()
        # SETUP.
        self.load_data()
        self.overlay = Overlay(self.player)

    def load_data(self):
        self.player = Player((640, 360), self.all_sprites)
        # GROUND.
        Generic(
            pos=(0, 0),
            surf=import_image("images", "world", "ground"),
            groups=self.all_sprites,
            z=LAYERS["ground"],
        )

    def run(self, dt):
        self.all_sprites.update(dt)
        self.all_sprites.draw(self.player)
        self.overlay.display()
