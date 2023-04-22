#!/usr/bin/env python3
from argparse import ArgumentParser

import pygame

from game import Game
from window import Window


def main(auto_start, auto_restart, width, height):
    pygame.init()

    window = Window(width, height)
    game = Game(grid_size=(16, 16), agents=[None, None])

    while True:
        # drawGrid()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return

        game.update()
        window.update()

        pygame.display.update()


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
