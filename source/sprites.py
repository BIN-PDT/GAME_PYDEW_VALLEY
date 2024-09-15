from random import randint, choice
import pygame
from settings import *
from timers import Timer


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
    def __init__(self, pos, surf, groups, name, stump_surf, apple_surf):
        super().__init__(pos, surf, groups)
        # TREE.
        self.health = 5 + (randint(0, 2) if name == "small" else randint(2, 4))
        self.is_alive = True
        self.stump_surf = stump_surf
        # FRUIT.
        self.apple_surf = apple_surf
        self.apple_offsets = APPLE_OFFSETS[name]
        self.apple_sprites = pygame.sprite.Group()
        self.spawn_apples()

    def spawn_apples(self):
        for offset_x, offset_y in self.apple_offsets:
            if randint(0, 10) < 2:
                pos = self.rect.left + offset_x, self.rect.top + offset_y
                Generic(
                    pos=pos,
                    surf=self.apple_surf,
                    groups=(self.apple_sprites, self.groups()[0]),
                    z=LAYERS["fruit"],
                )

    def get_damage(self):
        if self.is_alive:
            self.health -= 1
            # PICK AN APPLE.
            if self.apple_sprites:
                apple = choice(self.apple_sprites.sprites())
                apple.kill()
                # EFFECT.
                Particle(
                    pos=apple.rect.topleft,
                    surf=apple.image,
                    groups=self.groups()[0],
                    z=LAYERS["fruit"],
                )
            # CHECK DEATH.
            self.check_death()

    def check_death(self):
        if self.health <= 0:
            self.is_alive = False
            # EFFECT.
            Particle(
                pos=self.rect.topleft,
                surf=self.image,
                groups=self.groups()[0],
                z=LAYERS["fruit"],
                duration=300,
            )
            # CHANGE DISPLAY IMAGE.
            self.image = self.stump_surf
            self.rect = self.image.get_frect(midbottom=self.rect.midbottom)
            self.hitbox = self.rect.inflate(-10, -self.rect.height * 0.6)


class Particle(Generic):
    def __init__(self, pos, surf, groups, z, duration=200):
        super().__init__(pos, surf, groups, z)
        # SETUP.
        self.image = pygame.mask.from_surface(surf).to_surface()
        self.image.set_colorkey("black")
        # TIMER.
        self.life_timer = Timer(duration, self.kill, autostart=True)

    def update(self, _):
        self.life_timer.update()
