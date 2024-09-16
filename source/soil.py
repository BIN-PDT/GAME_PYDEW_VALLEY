import pygame
from os.path import join
from random import choice
from pytmx.util_pygame import load_pygame
from settings import *
from supports import *


class SoilLayer:
    def __init__(self, all_sprites, collision_sprites):
        # GROUPS.
        self.all_sprites = all_sprites
        self.collision_sprites = collision_sprites
        self.soil_sprites = pygame.sprite.Group()
        self.water_sprites = pygame.sprite.Group()
        self.plant_sprites = pygame.sprite.Group()
        # ASSETS.
        self.soil_surfs = import_folder_dict("images", "soil")
        self.water_surfs = import_folder_list("images", "soil_water")
        self.fruit_surfs = import_folder_dict("images", "fruit", subordinate=True)
        # SETUP.
        self.load_soil_grid()
        self.load_farmable_rects()
        # WEATHER.
        self.is_raining = None

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

    # EXCAVATE.
    def excavate(self, point):
        for rect in self.farmable_rects:
            if rect.collidepoint(point):
                area = self.grid[rect.y // TILE_SIZE][rect.x // TILE_SIZE]
                if "F" in area and "X" not in area:
                    area.append("X")
                    self.create_soil_tile()
                    # WATERED IF BEING RAINING.
                    if self.is_raining:
                        self.irrigate(point)
                    break

    def create_soil_tile(self):
        for sprite in self.soil_sprites.sprites():
            sprite.kill()

        for rect in self.farmable_rects:
            row_index, col_index = rect.y // TILE_SIZE, rect.x // TILE_SIZE
            if "X" in self.grid[row_index][col_index]:
                tile_type = self.type_soil_tile(row_index, col_index)
                SoilTile(
                    pos=(col_index * TILE_SIZE, row_index * TILE_SIZE),
                    surf=self.soil_surfs[tile_type],
                    groups=(self.all_sprites, self.soil_sprites),
                )

    def type_soil_tile(self, row_index, col_index):
        l = "X" in self.grid[row_index][col_index - 1]
        r = "X" in self.grid[row_index][col_index + 1]
        t = "X" in self.grid[row_index - 1][col_index]
        b = "X" in self.grid[row_index + 1][col_index]
        # ALL SIDES.
        if all((l, r, t, b)):
            return "x"
        # HORIZONTAL SIDE ONLY.
        if l and not any((r, t, b)):
            return "r"
        if r and not any((l, t, b)):
            return "l"
        if all((l, r)) and not any((t, b)):
            return "lr"
        # VERTICAL SIDE ONLY.
        if t and not any((l, r, b)):
            return "b"
        if b and not any((l, r, t)):
            return "t"
        if all((t, b)) and not any((l, r)):
            return "tb"
        # CORNER.
        if all((l, b)) and not any((r, t)):
            return "tr"
        if all((l, t)) and not any((r, b)):
            return "br"
        if all((r, b)) and not any((l, t)):
            return "tl"
        if all((r, t)) and not any((l, b)):
            return "bl"
        # T-SHAPE.
        if all((l, r, b)) and not t:
            return "lrt"
        if all((l, r, t)) and not b:
            return "lrb"
        if all((l, t, b)) and not r:
            return "tbl"
        if all((r, t, b)) and not l:
            return "tbr"
        # DEFAULT.
        return "o"

    # IRRIGATE.
    def irrigate(self, point):
        for sprite in self.soil_sprites.sprites():
            if sprite.rect.collidepoint(point):
                area = self.grid[sprite.rect.y // TILE_SIZE][sprite.rect.x // TILE_SIZE]
                if "X" in area and "W" not in area:
                    area.append("W")
                    WaterTile(
                        pos=sprite.rect.topleft,
                        surf=choice(self.water_surfs),
                        groups=(self.all_sprites, self.water_sprites),
                    )
                    break

    def irrigate_by_rain(self):
        for sprite in self.soil_sprites.sprites():
            area = self.grid[sprite.rect.y // TILE_SIZE][sprite.rect.x // TILE_SIZE]
            if "X" in area and "W" not in area:
                area.append("W")
                WaterTile(
                    pos=sprite.rect.topleft,
                    surf=choice(self.water_surfs),
                    groups=(self.all_sprites, self.water_sprites),
                )

    def absorb_water(self):
        for sprite in self.water_sprites.sprites():
            sprite.kill()

        for row in self.grid:
            for col in row:
                if "W" in col:
                    col.remove("W")

    def check_watered(self, pos):
        area = self.grid[pos[1] // TILE_SIZE][pos[0] // TILE_SIZE]
        return "W" in area

    # PLANT.
    def plant_seed(self, point, seed_type):
        for sprite in self.soil_sprites.sprites():
            if sprite.rect.collidepoint(point):
                area = self.grid[sprite.rect.y // TILE_SIZE][sprite.rect.x // TILE_SIZE]
                if "X" in area and "P" not in area:
                    area.append("P")
                    PlantTile(
                        frames=self.fruit_surfs[seed_type],
                        groups=(
                            self.all_sprites,
                            self.plant_sprites,
                            self.collision_sprites,
                        ),
                        plant_type=seed_type,
                        soil_sprite=sprite,
                        check_watered=self.check_watered,
                    )
                    break

    def grow_plants(self):
        for sprite in self.plant_sprites.sprites():
            sprite.grow()


class SoilTile(pygame.sprite.Sprite):
    def __init__(self, pos, surf, groups):
        super().__init__(groups)
        # SETUP.
        self.image = surf
        self.rect = self.image.get_rect(topleft=pos)
        self.z = LAYERS["soil"]


class WaterTile(pygame.sprite.Sprite):
    def __init__(self, pos, surf, groups):
        super().__init__(groups)
        # SETUP.
        self.image = surf
        self.rect = self.image.get_rect(topleft=pos)
        self.z = LAYERS["soil water"]


class PlantTile(pygame.sprite.Sprite):
    def __init__(self, frames, groups, plant_type, soil_sprite, check_watered):
        super().__init__(groups)
        # DATA.
        self.frames = frames
        self.plant_type = plant_type
        self.soil_sprite = soil_sprite
        self.check_watered = check_watered
        # GROWTH.
        self.MAX_AGE = len(self.frames) - 1
        self.age, self.speed = 0, GROW_SPEED[plant_type]
        self.is_harvestable = False
        # SETUP.
        self.image = self.frames[self.age]
        self.offset_y = Vector2(0, -16 if plant_type == "corn" else -8)
        self.rect = self.image.get_rect(
            midbottom=self.soil_sprite.rect.midbottom + self.offset_y
        )
        self.z = LAYERS["ground plant"]

    def grow(self):
        if self.check_watered(self.rect.center):
            self.age += self.speed
            # BECOME OBSTACLE.
            if self.age >= 1:
                self.z = LAYERS["main"]
                self.hitbox = self.rect.inflate(-26, -self.rect.height * 0.4)
            # CHECK HARVESTABLE.
            if self.age >= self.MAX_AGE:
                self.age = self.MAX_AGE
                self.is_harvestable = True
            # UPDATE.
            self.image = self.frames[int(self.age)]
            self.rect = self.image.get_rect(
                midbottom=self.soil_sprite.rect.midbottom + self.offset_y
            )
            self.hitbox = self.rect.inflate(-26, -self.rect.height * 0.4)
