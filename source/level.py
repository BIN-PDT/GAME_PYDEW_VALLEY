import pygame
from os.path import join
from pytmx.util_pygame import load_pygame
from settings import *
from supports import *

from groups import AllSprites
from player import Player
from overlay import Overlay
from sprites import *


class Level:
    def __init__(self):
        self.screen = pygame.display.get_surface()
        # GROUPS.
        self.all_sprites = AllSprites()
        self.collision_sprites = pygame.sprite.Group()
        # SETUP.
        self.load_data()
        self.overlay = Overlay(self.player)

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
        for obj in tmx_map.get_layer_by_name("Trees"):
            Tree(
                pos=(obj.x, obj.y),
                surf=obj.image,
                groups=(self.all_sprites, self.collision_sprites),
                name=obj.name,
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
                    )

    def run(self, dt):
        self.all_sprites.update(dt)
        self.all_sprites.draw(self.player)
        self.overlay.display()
