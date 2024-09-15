import pygame
from settings import *
from supports import import_folder_dict
from timers import Timer


class Player(pygame.sprite.Sprite):
    def __init__(self, pos, groups, collision_sprites):
        super().__init__(groups)
        self.load_assets()
        # ANIMATION.
        self.status = "down_idle"
        self.frame_index = 0
        self.ANIMATION_SPEED = 4
        # SETUP.
        self.image = self.animations[self.status][self.frame_index]
        self.rect = self.image.get_frect(center=pos)
        self.z = LAYERS["main"]
        # MOVEMENT.
        self.direction, self.speed = Vector2(), 200
        # COLLISION.
        self.collision_sprites = collision_sprites
        self.hitbox = self.rect.inflate((-126, -70))
        # TIMER.
        self.timers = {
            "tool_use": Timer(350, self.use_tool),
            "tool_switch": Timer(200),
            "seed_use": Timer(350, self.use_seed),
            "seed_switch": Timer(200),
        }
        # TOOL.
        self.tool_index = 0
        self.selected_tool = TOOL_CHOICES[self.tool_index]
        # SEED.
        self.seed_index = 0
        self.selected_seed = SEED_CHOICES[self.seed_index]

    def load_assets(self):
        self.animations = import_folder_dict("images", "character", subordinate=True)

    def use_tool(self):
        pass

    def use_seed(self):
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
            if keys[pygame.K_SPACE] and not self.timers["tool_use"].is_active:
                self.timers["tool_use"].activate()
                # RESET FOR ANIMATION.
                self.direction = Vector2()
                self.frame_index = 0
            # TOOL SWITCH.
            if keys[pygame.K_q] and not self.timers["tool_switch"].is_active:
                self.timers["tool_switch"].activate()

                self.tool_index += 1
                self.tool_index %= len(TOOL_CHOICES)
                self.selected_tool = TOOL_CHOICES[self.tool_index]
            # SEED USE.
            if keys[pygame.K_LCTRL] and not self.timers["seed_use"].is_active:
                self.timers["seed_use"].activate()
                # RESET FOR ANIMATION.
                self.direction = Vector2()
                self.frame_index = 0
            # SEED SWITCH.
            if keys[pygame.K_e] and not self.timers["seed_switch"].is_active:
                self.timers["seed_switch"].activate()

                self.seed_index += 1
                self.seed_index %= len(SEED_CHOICES)
                self.selected_seed = SEED_CHOICES[self.seed_index]

    def get_status(self):
        # IDLE.
        if not self.direction:
            self.status = self.status.split("_")[0] + "_idle"
        # TOOL USE.
        if self.timers["tool_use"].is_active:
            self.status = self.status.split("_")[0] + f"_{self.selected_tool}"

    def collide(self, direction):
        for sprite in filter(
            lambda sprite: hasattr(sprite, "hitbox"), self.collision_sprites.sprites()
        ):
            if self.hitbox.colliderect(sprite.hitbox):
                if direction == "horizontal":
                    if self.direction.x < 0:
                        self.hitbox.left = sprite.hitbox.right
                    elif self.direction.x > 0:
                        self.hitbox.right = sprite.hitbox.left
                    self.rect.centerx = self.hitbox.centerx
                else:
                    if self.direction.y < 0:
                        self.hitbox.top = sprite.hitbox.bottom
                    elif self.direction.y > 0:
                        self.hitbox.bottom = sprite.hitbox.top
                    self.rect.centery = self.hitbox.centery

    def move(self, dt):
        # NORMALIZE MOVEMENT.
        if self.direction:
            self.direction = self.direction.normalize()
        # HORIZONTAL MOVEMENT.
        self.rect.centerx += self.direction.x * self.speed * dt
        self.hitbox.centerx = self.rect.centerx
        self.collide("horizontal")
        # VERTICAL MOVEMENT.
        self.rect.centery += self.direction.y * self.speed * dt
        self.hitbox.centery = self.rect.centery
        self.collide("vertical")

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
