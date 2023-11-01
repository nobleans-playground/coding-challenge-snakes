#!/usr/bin/env python3

# Copyright 2023 Nobleo Technology B.V.
#
# SPDX-License-Identifier: Apache-2.0

import random
from argparse import ArgumentParser

import pygame

from snakes.window import Window


def main(auto_start, auto_restart, width, height, snake1, snake2, seed):
    pygame.init()
    pygame_display = pygame.display.set_mode((width, height))
    pygame.display.set_caption('Nobleo Snake Battle!')

    if seed is not None:
        random.seed(seed)

    window = Window(pygame_display, width, height, snake1, snake2)

    while True:
        for event in pygame.event.get():
            if event.type == pygame.MOUSEBUTTONDOWN:
                window.handle_click(pygame.mouse.get_pos())
            elif event.type == pygame.QUIT:
                pygame.quit()
                return

        window.update()
        pygame.display.update()
        window.sleep()


if __name__ == '__main__':
    parser = ArgumentParser(description='Nobleo Snakes')
    parser.add_argument('--auto-start', action='store_true',
                        help='Auto start the game')
    parser.add_argument('--auto-restart', type=int, default=None,
                        help='Auto restart the game after so many seconds')
    parser.add_argument('--width', type=int, default=1500,
                        help='width of the window')
    parser.add_argument('--height', type=int, default=1000,
                        help='height of the window')
    parser.add_argument('--snake1', '-s1', required=False, help="Name of snake 1")
    parser.add_argument('--snake2', '-s2', required=False, help="Name of snake 2")
    parser.add_argument('-s', '--seed', type=int, help='Random seed')
    args = parser.parse_args()

    try:
        main(**vars(args))
    except KeyboardInterrupt:
        pass
