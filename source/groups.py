import pygame
from settings import *


class AllSprites(pygame.sprite.Group):
    def __init__(self):
        super().__init__()
        self.screen = pygame.display.get_surface()
        # SETUP.
        self.offset = Vector2()

    def draw(self, player_pos):
        self.offset.x = -(player_pos[0] - SCREEN_WIDTH / 2)
        self.offset.y = -(player_pos[1] - SCREEN_HEIGHT / 2)

        for sprite in sorted(self, key=lambda sprite: (sprite.z, sprite.rect.centery)):
            self.screen.blit(sprite.image, sprite.rect.topleft + self.offset)
