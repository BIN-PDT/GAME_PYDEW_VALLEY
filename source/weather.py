import pygame
from random import randint, choice
from settings import *
from supports import *
from timers import Timer

from sprites import Generic


class Drop(Generic):
    def __init__(self, pos, surf, groups, z, can_move):
        super().__init__(pos, surf, groups, z)
        # MOVEMENT.
        self.can_move = can_move
        if self.can_move:
            self.direction = Vector2(-2, 4)
            self.speed = randint(200, 250)
        # TIMER.
        self.life_timer = Timer(randint(400, 500), self.kill, autostart=True)

    def update(self, dt):
        # TIMER.
        self.life_timer.update()
        # MOVEMENT.
        if self.can_move:
            self.rect.topleft += self.direction * self.speed * dt


class Rain:
    def __init__(self, all_sprites):
        # GROUP.
        self.all_sprites = all_sprites
        # SETUP.
        self.map_size = import_image("images", "world", "ground").get_size()
        self.rains_drops_surfs = import_folder_list("images", "rain", "drops")
        self.rains_floor_surfs = import_folder_list("images", "rain", "floor")

    def create_rain_floor(self):
        pos = randint(0, self.map_size[0]), randint(0, self.map_size[1])
        surf = choice(self.rains_floor_surfs)
        Drop(pos, surf, self.all_sprites, LAYERS["rain floor"], False)

    def create_rain_drops(self):
        pos = randint(0, self.map_size[0]), randint(0, self.map_size[1])
        surf = choice(self.rains_drops_surfs)
        Drop(pos, surf, self.all_sprites, LAYERS["rain drops"], True)

    def update(self):
        self.create_rain_floor()
        self.create_rain_drops()


class Sky:
    def __init__(self):
        self.screen = pygame.display.get_surface()
        # SETUP.
        self.image = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        self.NIGHT_MARK = (38, 101, 189)
        self.color = [255, 255, 255]

    def restart(self):
        self.color = [255, 255, 255]

    def display(self, dt):
        for index, value in enumerate(self.NIGHT_MARK):
            if self.color[index] > value:
                self.color[index] -= 2 * dt

        self.image.fill(self.color)
        self.screen.blit(self.image, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
