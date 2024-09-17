import pygame
from settings import *
from supports import import_folder_dict


class Overlay:
    def __init__(self, player):
        self.screen = pygame.display.get_surface()
        self.load_assets()
        # SETUP.
        self.player = player

    def load_assets(self):
        self.tool_surfs, self.seed_surfs = {}, {}

        overlays = import_folder_dict("images", "overlay")
        for item, surf in overlays.items():
            if item in TOOL_CHOICES:
                self.tool_surfs[item] = surf
            else:
                self.seed_surfs[item] = surf

    def display(self):
        # TOOL.
        tool_surf = self.tool_surfs[self.player.selected_tool]
        tool_rect = tool_surf.get_rect(midbottom=OVERLAY_POSITIONS["tool"])
        self.screen.blit(tool_surf, tool_rect)
        # SEED.
        seed_surf = self.seed_surfs[self.player.selected_seed]
        seed_rect = seed_surf.get_rect(midbottom=OVERLAY_POSITIONS["seed"])
        self.screen.blit(seed_surf, seed_rect)
