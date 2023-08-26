import math
import pygame


BLACK = (0, 0, 0)
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

TEAM_A = (230, 25, 75)
TEAM_B = (60, 180, 75)

class Window:
    def __init__(self, window, game, width, height):
        self.game = game
        self.window = window
        self.width = width
        self.height = height

        # Some GUI stuff
        pygame.font.init()
        self.font = pygame.font.SysFont(None, 24)
        self.buttons = []

        # The scoreboard is where all the scores will be printed
        self.scoreboard = pygame.Surface(self.window.get_size())
        self.font = pygame.font.SysFont(None, 24)

        # Create some constants (assuming area is square)
        self.tile_size = math.floor(min(self.window.get_size()) / self.game.grid_size[1])
        self.body_size = math.floor(self.tile_size * 0.9)
        self.body_tile_offset = (self.tile_size - self.body_size) / 2
        self.candy_radius = int(self.tile_size * 0.6 / 2)

    class Button:
        def __init__(self, surface, **kwargs):
            def extract(key):
                return kwargs[key] or RuntimeError(f"No `{key}` given to button")
            self.position = extract("position")
            self.width = extract("width")
            self.height = extract("height")
            self.text = extract("text")
            self.callback = extract("callback")         

            text_object = self.font.render(self.text, True, self.WHITE + (50,))
            self.scoreboard.blit(text_object, self.position)

    def button(self, **kwargs):
        self.buttons += [self.Button(kwargs)]

    def update(self):
        self.window.fill(BLACK)

        self.update_information()

        # Draw snake
        for snake in self.game.snakes:
            for position in snake:
                pygame.draw.rect(self.window, COLOURS[snake.id], (
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

    def update_information(self):
        # Draw the information part
        border = 5
        left = self.height + border
        right = self.width - border
        top = border

        player_emblem_height = 60

        for index, colour in enumerate([TEAM_A, TEAM_B]):
            if index >= len(self.game.snakes): continue

            pygame.draw.rect(self.window, colour, (left, top, right - left, player_emblem_height))

            # Draw Name
            text_to_render = self.game.agents[index].name
            font = pygame.font.SysFont(None, 32)
            text_object = font.render(text_to_render, True, WHITE)
            self.window.blit(text_object, (left + border, top + border))

            # Draw score
            font = pygame.font.SysFont(None, 68)
            text_to_render = f"{len(self.game.snakes[index])}"
            text_size = font.size(text_to_render)
            text_object = font.render(text_to_render, True, WHITE)
            self.window.blit(text_object, (right - border - text_size[0], top + border))

            top += player_emblem_height + border