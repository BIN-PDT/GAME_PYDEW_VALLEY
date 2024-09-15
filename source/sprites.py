import pygame
from settings import *


class Generic(pygame.sprite.Sprite):
    def __init__(self, pos, surf, groups, z=LAYERS["main"]):
        super().__init__(groups)
        # SETUP.
        self.image = surf
        self.rect = self.image.get_frect(topleft=pos)
        self.z = z
        # COLLISION.
        self.hitbox = self.rect.inflate(
            (-self.rect.width * 0.2, -self.rect.height * 0.75)
        )


class Water(Generic):
    def __init__(self, pos, frames, groups):
        # ANIMATION.
        self.frames = frames
        self.frame_index = 0

        super().__init__(
            pos=pos,
            surf=self.frames[self.frame_index],
            groups=groups,
            z=LAYERS["water"],
        )

    def animate(self, dt):
        self.frame_index += 5 * dt
        self.frame_index %= len(self.frames)

        self.image = self.frames[int(self.frame_index)]

    def update(self, dt):
        self.animate(dt)


class WildFlower(Generic):
    def __init__(self, pos, surf, groups):
        super().__init__(pos, surf, groups)
        # COLLISION.
        self.hitbox = self.rect.inflate((-20, -self.rect.height * 0.9))


class Tree(Generic):
    def __init__(self, pos, surf, groups, name):
        super().__init__(pos, surf, groups)
