import pygame
from os.path import join
from pytmx.util_pygame import load_pygame
from settings import *
from supports import *


class SoilLayer:
    def __init__(self, all_sprites):
        # GROUPS.
        self.all_sprites = all_sprites
        self.soil_sprites = pygame.sprite.Group()
        # ASSETS.
        self.soil_surf = import_image("images", "soil", "o")
        # SETUP.
        self.load_soil_grid()
        self.load_farmable_rects()

    def load_soil_grid(self):
        # CREATE GRID.
        ground_surf = import_image("images", "world", "ground")
        self.grid = [
            [[] for _ in range(ground_surf.get_width() // TILE_SIZE)]
            for _ in range(ground_surf.get_height() // TILE_SIZE)
        ]
        # MARK THE FARMABLE CELL.
        tmx_map = load_pygame(join("data", "map.tmx"))
        for x, y, _ in tmx_map.get_layer_by_name("Farmable").tiles():
            self.grid[y][x].append("F")

    def load_farmable_rects(self):
        self.farmable_rects = []
        # CREATE THE FARMABLE RECT.
        for row_index, row in enumerate(self.grid):
            for col_index, col in enumerate(row):
                if "F" in col:
                    x, y = col_index * TILE_SIZE, row_index * TILE_SIZE
                    rect = pygame.Rect(x, y, TILE_SIZE, TILE_SIZE)
                    self.farmable_rects.append(rect)

    def excavate(self, point):
        for rect in self.farmable_rects:
            if rect.collidepoint(point):
                area = self.grid[rect.y // TILE_SIZE][rect.x // TILE_SIZE]
                if "F" in area and "X" not in area:
                    area.append("X")
                    self.create_soil_tile()
                    break

    def create_soil_tile(self):
        self.soil_sprites.empty()
        for row_index, row in enumerate(self.grid):
            for col_index, col in enumerate(row):
                if "X" in col:
                    SoilTile(
                        pos=(col_index * TILE_SIZE, row_index * TILE_SIZE),
                        surf=self.soil_surf,
                        groups=(self.all_sprites, self.soil_sprites),
                    )


class SoilTile(pygame.sprite.Sprite):
    def __init__(self, pos, surf, groups):
        super().__init__(groups)
        # SETUP.
        self.image = surf
        self.rect = self.image.get_rect(topleft=pos)
        self.z = LAYERS["soil"]
