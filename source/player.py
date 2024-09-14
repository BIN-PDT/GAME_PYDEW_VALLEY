import pygame
from settings import *
from supports import import_folder_dict
from timers import Timer


class Player(pygame.sprite.Sprite):
    def __init__(self, pos, groups):
        super().__init__(groups)
        self.load_assets()
        # ANIMATION.
        self.status = "down_idle"
        self.frame_index = 0
        self.ANIMATION_SPEED = 4
        # SETUP.
        self.image = self.animations[self.status][self.frame_index]
        self.rect = self.image.get_frect(center=pos)
        # MOVEMENT.
        self.direction, self.speed = Vector2(), 200
        # TIMER.
        self.timers = {"tool_use": Timer(350, self.use_tool)}
        # TOOL.
        self.selected_tool = "water"

    def load_assets(self):
        self.animations = import_folder_dict("images", "character", subordinate=True)

    def use_tool(self):
        pass

    def input(self):
        keys = pygame.key.get_pressed()

        if not self.timers["tool_use"].is_active:
            # HORIZONTAL MOVEMENT.
            if keys[pygame.K_LEFT]:
                self.direction.x = -1
                self.status = "left"
            elif keys[pygame.K_RIGHT]:
                self.direction.x = 1
                self.status = "right"
            else:
                self.direction.x = 0
            # VERTICAL MOVEMENT.
            if keys[pygame.K_UP]:
                self.direction.y = -1
                self.status = "up"
            elif keys[pygame.K_DOWN]:
                self.direction.y = 1
                self.status = "down"
            else:
                self.direction.y = 0
            # TOOL USE.
            if keys[pygame.K_SPACE]:
                self.timers["tool_use"].activate()
                # RESET FOR ANIMATION.
                self.direction = Vector2()
                self.frame_index = 0

    def get_status(self):
        # IDLE.
        if not self.direction:
            self.status = self.status.split("_")[0] + "_idle"
        # TOOL USE.
        if self.timers["tool_use"].is_active:
            self.status = self.status.split("_")[0] + f"_{self.selected_tool}"

    def move(self, dt):
        # NORMALIZE MOVEMENT.
        if self.direction:
            self.direction = self.direction.normalize()
        # HORIZONTAL MOVEMENT.
        self.rect.centerx += self.direction.x * self.speed * dt
        # VERTICAL MOVEMENT.
        self.rect.centery += self.direction.y * self.speed * dt

    def animate(self, dt):
        ANIMATION = self.animations[self.status]
        self.frame_index += self.ANIMATION_SPEED * dt

        self.frame_index %= len(ANIMATION)
        self.image = ANIMATION[int(self.frame_index)]

    def update_timers(self):
        for timer in self.timers.values():
            timer.update()

    def update(self, dt):
        self.update_timers()
        self.input()
        self.get_status()
        self.move(dt)
        self.animate(dt)
