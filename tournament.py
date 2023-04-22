#!/usr/bin/env python3
from argparse import ArgumentParser

import numpy as np

from bots import Random
from game import Game


class Printer:
    def print(self, game):
        grid = np.empty(game.grid_size, dtype=np.unicode)
        for x in range(game.grid_size[0]):
            for y in range(game.grid_size[1]):
                grid[x, y] = ' '
        for snake in game.snakes:
            print(f'snake={snake}')
            for pos in snake:
                grid[pos[0], pos[1]] = str(snake.id)
        print(grid)


def main():
    agents = [Random(), Random()]
    game = Game(grid_size=(16, 16), agents=agents)
    printer = Printer()
    for i in range(5):
        game.update()
        printer.print(game)


if __name__ == '__main__':
    parser = ArgumentParser(description='Nobleo Snakes')
    args = parser.parse_args()

    try:
        main(**vars(args))
    except KeyboardInterrupt:
        pass
