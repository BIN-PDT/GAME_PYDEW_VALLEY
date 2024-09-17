import pygame
from settings import *
from supports import import_folder_dict
from timers import Timer


class Player(pygame.sprite.Sprite):
    def __init__(
        self,
        pos,
        groups,
        collision_sprites,
        tree_sprites,
        interaction_sprites,
        soil_layer,
        toggle_shop,
        hoe_sound,
        water_sound,
        plant_sound,
    ):
        super().__init__(groups)
        # ANIMATION.
        self.animations = import_folder_dict("images", "character", subordinate=True)
        self.status = "down_idle"
        self.frame_index = 0
        # SETUP.
        self.image = self.animations[self.status][self.frame_index]
        self.rect = self.image.get_frect(center=pos)
        self.z = LAYERS["main"]
        # MOVEMENT.
        self.direction = Vector2()
        self.speed = 200
        # COLLISION.
        self.collision_sprites = collision_sprites
        self.hitbox = self.rect.inflate(-126, -70)
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
        # INVENTORY.
        self.item_inventory = {"wood": 0, "apple": 0, "corn": 0, "tomato": 0}
        self.seed_inventory = {"corn": 5, "tomato": 5}
        self.money = 200
        # INTERACTION.
        self.tree_sprites = tree_sprites
        self.interaction_sprites = interaction_sprites
        # RESTART DAY.
        self.is_sleeping = False
        # SOIL PLAYER.
        self.soil_layer = soil_layer
        # SHOP.
        self.toggle_shop = toggle_shop
        # AUDIO.
        self.hoe_sound = hoe_sound
        self.water_sound = water_sound
        self.plant_sound = plant_sound

    @property
    def target_pos(self):
        return self.rect.center + PLAYER_TOOL_OFFSET[self.status.split("_")[0]]

    def use_tool(self):
        match self.selected_tool:
            case "hoe":
                self.soil_layer.excavate(self.target_pos)
                # PLAY SOUND.
                self.hoe_sound.play()
            case "water":
                self.soil_layer.irrigate(self.target_pos)
                # PLAY SOUND.
                self.water_sound.play()
            case "axe":
                for sprite in self.tree_sprites.sprites():
                    if sprite.rect.collidepoint(self.target_pos):
                        sprite.get_damage()

    def use_seed(self):
        if self.seed_inventory[self.selected_seed] > 0:
            self.seed_inventory[self.selected_seed] -= 1
            self.soil_layer.plant_seed(self.target_pos, self.selected_seed)
            # PLAY SOUND.
            self.plant_sound.play()

    def input(self):
        if not self.timers["tool_use"].is_active and not self.is_sleeping:
            keys = pygame.key.get_pressed()
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
            # INTERACTION.
            if keys[pygame.K_RETURN]:
                collided_sprites = pygame.sprite.spritecollide(
                    self, self.interaction_sprites, False
                )
                if collided_sprites:
                    collided_sprite = collided_sprites[0]
                    # INTERACT WITH BED.
                    if collided_sprite.name == "Bed":
                        self.status = "left_idle"
                        self.is_sleeping = True
                    # INTERACT WITH TRADER.
                    else:
                        self.toggle_shop()

    def get_status(self):
        # IDLE.
        if not self.direction:
            self.status = f"{self.status.split('_')[0]}_idle"
        # USE TOOL.
        if self.timers["tool_use"].is_active:
            self.status = f"{self.status.split('_')[0]}_{self.selected_tool}"

    def collide(self, direction):
        for sprite in self.collision_sprites:
            if hasattr(sprite, "hitbox"):
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
        animation = self.animations[self.status]
        self.frame_index += 4 * dt
        self.frame_index %= len(animation)

        self.image = animation[int(self.frame_index)]

    def update_timers(self):
        for timer in self.timers.values():
            timer.update()

    def update(self, dt):
        self.update_timers()
        self.input()
        self.get_status()
        self.move(dt)
        self.animate(dt)
