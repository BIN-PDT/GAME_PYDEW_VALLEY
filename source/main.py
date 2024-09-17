import pygame
from sys import exit
from settings import *
from level import Level


class Game:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Pydew Valley")
        self.clock = pygame.time.Clock()
        self.level = Level()

    def run(self):
        while True:
            dt = self.clock.tick() / 1000
            # EVENT LOOP.
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    exit()
            # GAME LOGIC.
            self.screen.fill("black")
            self.level.run(dt)
            pygame.display.update()


if __name__ == "__main__":
    Game().run()
