import math

import pygame

WHITE = (255, 255, 255)
RED = (255, 0, 0)

COLOURS = [
    (230, 25, 75),
    (60, 180, 75),
    (255, 225, 25),
    (0, 130, 200),
    (245, 130, 48),
    (145, 30, 180),
    (70, 240, 240),
    (240, 50, 230),
    (210, 245, 60),
    (250, 190, 212),
    (0, 128, 128),
    (220, 190, 255),
    (170, 110, 40),
    (255, 250, 200),
    (128, 0, 0),
    (170, 255, 195),
    (128, 128, 0),
    (255, 215, 180),
    (0, 0, 128),
    (128, 128, 128),
]


class Window:
    def __init__(self, window, game, width, height):
        self.game = game
        self.window = window

        # The scoreboard is where all the scores will be printed
        self.scoreboard = pygame.Surface(self.window.get_size())
        self.font = pygame.font.SysFont(None, 24)

        # Create some constants (assuming area is square)
        self.tile_size = math.floor(min(self.window.get_size()) / self.game.grid_size[1])
        self.body_size = math.floor(self.tile_size * 0.9)
        self.body_tile_offset = (self.tile_size - self.body_size) / 2
        self.candy_radius = int(self.tile_size * 0.6 / 2)

    def update(self):
        BLACK = (0, 0, 0)
        self.window.fill(BLACK)

        # Draw snake
        for index, snake in enumerate(self.game.snakes):
            for position in snake:
                pygame.draw.rect(self.window, COLOURS[index], (
                    (position[0] * self.tile_size) + self.body_tile_offset,
                    (position[1] * self.tile_size) + self.body_tile_offset,
                    self.body_size, self.body_size
                ))

        # Draw candies
        for candy in self.game.candies:
            pygame.draw.circle(self.window, COLOURS[-1], (
                int((candy[0] + 0.5) * self.tile_size),
                int((candy[1] + 0.5) * self.tile_size),
            ), self.candy_radius)
