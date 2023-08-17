#!/usr/bin/env python3
from argparse import ArgumentParser
from math import isinf
from time import sleep

import numpy as np

from bots import bots
from game import Game, RoundType


class Printer:
    def print(self, game):
        grid = np.empty(game.grid_size, dtype=str)
        for x in range(game.grid_size[0]):
            for y in range(game.grid_size[1]):
                grid[x, y] = ' '
        for snake in game.snakes:
            print(f'name={game.agents[snake.id].name!r} {snake}')
            for pos in snake:
                grid[pos[0], pos[1]] = str(snake.id)
        for candy in game.candies:
            grid[candy[0], candy[1]] = '*'
        print(np.flipud(grid.T))


def main(rate):
    grid_size = (16, 8)
    agents = {i: Bot(id=i, grid_size=grid_size) for i, Bot in enumerate(bots)}
    game = Game(grid_size=grid_size, agents=agents, round_type=RoundType.TURNS)
    printer = Printer()
    printer.print(game)
    while True:
        game.update()
        printer.print(game)
        if not isinf(rate):
            sleep(1 / rate)

        if game.finished():
            break

    print('Name\tFinal position')
    for id, score in game.scores.items():
        print(f'{game.agents[id].name}\t{score}')


if __name__ == '__main__':
    parser = ArgumentParser(description='Nobleo Snakes')
    parser.add_argument('-r', '--rate', default=float('inf'), type=float, help="Playback rate (Hz)")
    args = parser.parse_args()

    try:
        main(**vars(args))
    except KeyboardInterrupt:
        pass
