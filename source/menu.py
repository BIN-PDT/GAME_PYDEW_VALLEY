import pygame
from os.path import join
from settings import *


class Menu:
    def __init__(self, player, toggle_shop):
        self.screen = pygame.display.get_surface()
        # DATA.
        self.player = player
        self.toggle_shop = toggle_shop
        # UI.
        self.font = pygame.font.Font(join("font", "LycheeSoda.ttf"), 30)
        self.WIDTH = 400
        self.SPACING, self.PADDING = 20, 8
        # ENTRIES.
        self.OPTIONS = list(self.player.item_inventory) + list(
            self.player.seed_inventory
        )
        self.SELLABLE_BORDER = len(list(self.player.item_inventory)) - 1
        # SELECTION.
        self.selected_index = 0
        # SETUP.
        self.load_data()

    def load_data(self):
        # OPTION INFORMATION.
        self.text_surfs = []
        total_height = 0

        for option in self.OPTIONS:
            text_surf = self.font.render(option, False, "black")
            self.text_surfs.append(text_surf)

            total_height += text_surf.get_height() + 2 * self.PADDING
        total_height += (len(self.text_surfs) - 1) * self.SPACING

        offset_left = (SCREEN_WIDTH - self.WIDTH) / 2
        self.offset_top = (SCREEN_HEIGHT - total_height) / 2
        self.main_rect = pygame.Rect(
            offset_left, self.offset_top, self.WIDTH, total_height
        )
        # BUY/SELL INFORMATION.
        self.buy_text_surf = self.font.render("buy", False, "black")
        self.sell_text_surf = self.font.render("sell", False, "black")

    def input(self):
        keys = pygame.key.get_just_pressed()
        # CLOSE.
        if keys[pygame.K_ESCAPE]:
            self.toggle_shop()
        # SWITCH.
        if keys[pygame.K_UP]:
            self.selected_index -= 1
        elif keys[pygame.K_DOWN]:
            self.selected_index += 1
        elif keys[pygame.K_SPACE]:
            # SELL.
            selected_option = self.OPTIONS[self.selected_index]
            if self.selected_index <= self.SELLABLE_BORDER:
                if self.player.item_inventory[selected_option] > 0:
                    self.player.item_inventory[selected_option] -= 1
                    self.player.money += SALE_PRICES[selected_option]
            # BUY.
            else:
                if self.player.money >= PURCHASE_PRICES[selected_option]:
                    self.player.seed_inventory[selected_option] += 1
                    self.player.money -= PURCHASE_PRICES[selected_option]
        # SWITCH CONSTRAINT.
        self.selected_index %= len(self.OPTIONS)

    def display_money(self):
        text_surf = self.font.render(f"${self.player.money}", False, "black")
        text_rect = text_surf.get_rect(midbottom=(SCREEN_WIDTH / 2, SCREEN_HEIGHT - 20))

        pygame.draw.rect(self.screen, "white", text_rect.inflate(20, 10), 0, 5)
        self.screen.blit(text_surf, text_rect)

    def display_entries(self):
        AMOUNTS = list(self.player.item_inventory.values()) + list(
            self.player.seed_inventory.values()
        )
        for index, text_surf in enumerate(self.text_surfs):
            offset_top = self.main_rect.top + index * (
                text_surf.get_height() + 2 * self.PADDING + self.SPACING
            )

            self.display_entry(
                offset_top=offset_top,
                text_surf=text_surf,
                amount=AMOUNTS[index],
                is_selected=self.selected_index == index,
            )

    def display_entry(self, offset_top, text_surf, amount, is_selected):
        # BACKGROUND.
        bg_rect = pygame.Rect(
            self.main_rect.left,
            offset_top,
            self.WIDTH,
            text_surf.get_height() + 2 * self.PADDING,
        )
        pygame.draw.rect(self.screen, "white", bg_rect, 0, 5)
        # TEXT.
        text_rect = text_surf.get_rect(midleft=bg_rect.midleft + Vector2(20, 0))
        self.screen.blit(text_surf, text_rect)
        # AMOUNT.
        amount_surf = self.font.render(str(amount), False, "black")
        amount_rect = amount_surf.get_rect(midright=bg_rect.midright + Vector2(-20, 0))
        self.screen.blit(amount_surf, amount_rect)
        # SELECTED STATE.
        if is_selected:
            # BODER.
            pygame.draw.rect(self.screen, "black", bg_rect, 5, 5)
            # BUY/SELL INFORMATION.
            info_surf = (
                self.sell_text_surf
                if self.selected_index <= self.SELLABLE_BORDER
                else self.buy_text_surf
            )
            info_rect = info_surf.get_rect(midleft=bg_rect.midleft + Vector2(180, 0))
            self.screen.blit(info_surf, info_rect)

    def update(self):
        self.input()
        self.display_money()
        self.display_entries()
