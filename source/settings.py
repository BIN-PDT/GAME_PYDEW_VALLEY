from pygame.math import Vector2

# SCREEN.
SCREEN_WIDTH = 1280
SCREEN_HEIGHT = 720
TILE_SIZE = 64
# OVERLAY POSITIONS.
OVERLAY_POSITIONS = {
    "tool": (40, SCREEN_HEIGHT - 15),
    "seed": (70, SCREEN_HEIGHT - 5),
}
PLAYER_TOOL_OFFSET = {
    "up": Vector2(0, -10),
    "down": Vector2(0, 50),
    "left": Vector2(-50, 40),
    "right": Vector2(50, 40),
}
APPLE_OFFSETS = {
    "small": [(18, 17), (30, 37), (12, 50), (30, 45), (20, 30), (30, 10)],
    "large": [(30, 24), (60, 65), (50, 50), (16, 40), (45, 50), (42, 70)],
}
LAYERS = {
    "water": 0,
    "ground": 1,
    "soil": 2,
    "soil water": 3,
    "rain floor": 4,
    "house bottom": 5,
    "ground plant": 6,
    "main": 7,
    "house top": 8,
    "fruit": 9,
    "rain drops": 10,
}
# GAME DATA.
TOOL_CHOICES = ("hoe", "axe", "water")
SEED_CHOICES = ("corn", "tomato")
GROW_SPEED = {"corn": 1, "tomato": 0.7}
SALE_PRICES = {"wood": 4, "apple": 2, "corn": 10, "tomato": 20}
PURCHASE_PRICES = {"corn": 4, "tomato": 5}
