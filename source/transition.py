import pygame as pg
from settings import *


class Transition:
    def __init__(self, player, restart_day):
        self.screen = pg.display.get_surface()
        # SETUP.
        self.image = pg.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        self.color, self.speed = 255, -2

        self.player = player
        self.restart_day = restart_day

    def display(self):
        self.color += self.speed
        # GO TO BED.
        if self.color < 0:
            self.color = 0
            self.speed *= -1
            self.restart_day()
            self.player.status = "down_idle"
        # WAKE UP.
        elif self.color > 255:
            self.color = 255
            self.speed *= -1
            self.player.is_sleeping = False
        self.image.fill((self.color, self.color, self.color))
        self.screen.blit(self.image, (0, 0), special_flags=pg.BLEND_RGBA_MULT)
