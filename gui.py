#!/usr/bin/env python3
import time
from argparse import ArgumentParser

import pygame

from snakes.bots import bots
from snakes.game import Game
from snakes.window import Window


def main(auto_start, auto_restart, width, height):
    pygame.init()
    pygame_display = pygame.display.set_mode((width, height))
    pygame.display.set_caption('Nobleo Snake Battle!')

    grid_size = (16, 16)
    agents = {i: Bot(id=i, grid_size=grid_size) for i, Bot in enumerate(bots) if i < 2}
    game = Game(grid_size=grid_size, agents=agents)
    window = Window(pygame_display, game, width, height)

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return

        game.update()
        window.update()

        pygame.display.update()
        time.sleep(0.1)


if __name__ == '__main__':
    parser = ArgumentParser(description='Nobleo Snakes')
    parser.add_argument('--auto-start', action='store_true',
                        help='Auto start the game')
    parser.add_argument('--auto-restart', type=int, default=None,
                        help='Auto restart the game after so many seconds')
    parser.add_argument('--width', type=int, default=1150,
                        help='width of the window')
    parser.add_argument('--height', type=int, default=700,
                        help='height of the window')
    args = parser.parse_args()

    try:
        main(**vars(args))
    except KeyboardInterrupt:
        pass
