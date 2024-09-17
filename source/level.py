import pygame
from os.path import join
from random import randint
from pytmx.util_pygame import load_pygame
from settings import *
from supports import *
from timers import Timer

from groups import AllSprites
from player import Player
from overlay import Overlay
from sprites import *
from transition import Transition
from soil import SoilLayer
from weather import Rain, Sky
from menu import Menu


class Level:
    def __init__(self):
        self.screen = pygame.display.get_surface()
        # GROUPS.
        self.all_sprites = AllSprites()
        self.collision_sprites = pygame.sprite.Group()
        self.tree_sprites = pygame.sprite.Group()
        self.interaction_sprites = pygame.sprite.Group()
        # AUDIO.
        self.sounds = import_audio("audio")
        self.sounds["bg"].set_volume(0.5)
        self.sounds["success"].set_volume(0.3)
        self.sounds["hoe"].set_volume(0.1)
        self.sounds["water"].set_volume(0.2)
        self.sounds["plant"].set_volume(0.2)
        # TIMER.
        self.shop_timer = Timer(250)
        # SETUP.
        self.soil_layer = SoilLayer(self.all_sprites, self.collision_sprites)
        self.load_data()
        self.overlay = Overlay(self.player)
        self.transition = Transition(self.player, self.restart_day)
        # WEATHER.
        self.rain = Rain(self.all_sprites)
        self.is_raining = randint(0, 10) > 5
        self.soil_layer.is_raining = self.is_raining
        self.sky = Sky()
        # SHOP.
        self.shop_active = False
        self.menu = Menu(self.player, self.toggle_shop)
        # BACKGROUND MUSIC.
        self.sounds["bg"].play(-1)

    def load_data(self):
        tmx_map = load_pygame(join("data", "map.tmx"))
        # GROUND.
        Generic(
            pos=(0, 0),
            surf=import_image("images", "world", "ground"),
            groups=self.all_sprites,
            z=LAYERS["ground"],
        )
        # HOUSE.
        for layer in ("HouseFloor", "HouseFurnitureBottom"):
            for x, y, surf in tmx_map.get_layer_by_name(layer).tiles():
                Generic(
                    pos=(x * TILE_SIZE, y * TILE_SIZE),
                    surf=surf,
                    groups=self.all_sprites,
                    z=LAYERS["house bottom"],
                )
        for layer in ("HouseWalls", "HouseFurnitureTop"):
            for x, y, surf in tmx_map.get_layer_by_name(layer).tiles():
                Generic(
                    pos=(x * TILE_SIZE, y * TILE_SIZE),
                    surf=surf,
                    groups=self.all_sprites,
                )
        # FENCE.
        for x, y, surf in tmx_map.get_layer_by_name("Fence").tiles():
            Generic(
                pos=(x * TILE_SIZE, y * TILE_SIZE),
                surf=surf,
                groups=(self.all_sprites, self.collision_sprites),
            )
        # WATER.
        frames = import_folder_list("images", "water")
        for x, y, _ in tmx_map.get_layer_by_name("Water").tiles():
            Water(
                pos=(x * TILE_SIZE, y * TILE_SIZE),
                frames=frames,
                groups=self.all_sprites,
            )
        # WILDFLOWER.
        for obj in tmx_map.get_layer_by_name("Decoration"):
            WildFlower(
                pos=(obj.x, obj.y),
                surf=obj.image,
                groups=(self.all_sprites, self.collision_sprites),
            )
        # TREE.
        stump_surfs = import_folder_dict("images", "stumps")
        apple_surf = import_image("images", "fruit", "apple")
        for obj in tmx_map.get_layer_by_name("Trees"):
            name = obj.name.lower()
            Tree(
                pos=(obj.x, obj.y),
                surf=obj.image,
                groups=(self.all_sprites, self.collision_sprites, self.tree_sprites),
                name=name,
                stump_surf=stump_surfs[name],
                apple_surf=apple_surf,
                add_item_to_player=self.add_item_to_player,
                axe_sound=self.sounds["axe"],
            )
        # CONSTRAINT TILE.
        for x, y, surf in tmx_map.get_layer_by_name("Collision").tiles():
            Generic(
                pos=(x * TILE_SIZE, y * TILE_SIZE),
                surf=surf,
                groups=self.collision_sprites,
            )
        # PLAYER & INTERACTIVE OBJECT.
        for obj in tmx_map.get_layer_by_name("Player"):
            match obj.name:
                case "Start":
                    self.player = Player(
                        pos=(obj.x, obj.y),
                        groups=self.all_sprites,
                        collision_sprites=self.collision_sprites,
                        tree_sprites=self.tree_sprites,
                        interaction_sprites=self.interaction_sprites,
                        soil_layer=self.soil_layer,
                        toggle_shop=self.toggle_shop,
                        hoe_sound=self.sounds["hoe"],
                        water_sound=self.sounds["water"],
                        plant_sound=self.sounds["plant"],
                    )
                case "Bed":
                    Interaction(
                        pos=(obj.x, obj.y),
                        size=(obj.width, obj.height),
                        groups=self.interaction_sprites,
                        name=obj.name,
                    )
                case "Trader":
                    Interaction(
                        pos=(obj.x, obj.y),
                        size=(obj.width, obj.height),
                        groups=self.interaction_sprites,
                        name=obj.name,
                    )

    def toggle_shop(self):
        if not self.shop_timer.is_active:
            self.shop_timer.activate()
            self.shop_active = not self.shop_active

    def add_item_to_player(self, item):
        self.player.item_inventory[item] += 1
        # PLAY SOUND.
        self.sounds["success"].play()

    def check_plant_harvest(self):
        for sprite in self.soil_layer.plant_sprites.sprites():
            if sprite.is_harvestable and sprite.rect.colliderect(self.player.hitbox):
                sprite.kill()
                # REMOVE FROM SOIL GRID.
                self.soil_layer.grid[sprite.rect.centery // TILE_SIZE][
                    sprite.rect.centerx // TILE_SIZE
                ].remove("P")
                # EFFECT.
                Particle(
                    pos=sprite.rect.topleft,
                    surf=sprite.image,
                    groups=self.all_sprites,
                    z=LAYERS["main"],
                )
                # PLAYER INVENTORY.
                self.add_item_to_player(sprite.plant_type)

    def restart_day(self):
        # RESET TREE.
        for tree in self.tree_sprites.sprites():
            tree.spawn_apples()
        # DAY & NIGHT.
        self.sky.restart()
        # SOIL LAYER.
        self.soil_layer.grow_plants()
        self.soil_layer.absorb_water()
        # WEATHER.
        self.is_raining = randint(0, 10) > 5
        self.soil_layer.is_raining = self.is_raining
        if self.is_raining:
            self.soil_layer.irrigate_by_rain()

    def run(self, dt):
        self.shop_timer.update()

        self.all_sprites.draw(self.player.rect.center)
        self.overlay.display()
        # SHOP.
        if self.shop_active:
            self.menu.update()
        else:
            self.all_sprites.update(dt)
            # HARVEST.
            self.check_plant_harvest()
            # WEATHER.
            if self.is_raining:
                self.rain.update()
            # RESTART DAY.
            if self.player.is_sleeping:
                self.transition.display()
        # DAY & NIGHT.
        self.sky.display(dt)
