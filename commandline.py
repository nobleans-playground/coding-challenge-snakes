#!/usr/bin/env python3

# Copyright 2023 Nobleo Technology B.V.
#
# SPDX-License-Identifier: Apache-2.0

from argparse import ArgumentParser
from math import isinf
from time import sleep

import numpy as np

from snakes.bots import bots
from snakes.game import Game, RoundType
from snakes.utils import levenshtein_ratio


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


def main(snake1, snake2, rate):
    names = [Bot(id=i, grid_size=(1, 1)).name for i, Bot in enumerate(bots)]

    name_matches = [levenshtein_ratio(name, snake1) for name in names]
    agent1 = np.argmax(name_matches)

    name_matches = [levenshtein_ratio(name, snake2) for name in names]
    agent2 = np.argmax(name_matches)

    # One agent could be up against itself, so we'll need to give new ids
    agents = {0: bots[agent1], 1: bots[agent2]}

    game = Game(agents=agents, round_type=RoundType.TURNS)
    printer = Printer()
    printer.print(game)
    while True:
        game.update()
        printer.print(game)
        if not isinf(rate):
            sleep(1 / rate)

        if game.finished():
            break

    print(f'{"Id":4}{"Name":20} Final position')
    for id, rank in game.rank().items():
        print(f'{id:<4}{game.agents[id].name:20} {rank}')


if __name__ == '__main__':
    parser = ArgumentParser(description='Battle two snakes in the command line')
    parser.add_argument('snake1', help="Name of snake 1")
    parser.add_argument('snake2', help="Name of snake 2")
    parser.add_argument('-r', '--rate', default=float('inf'), type=float, help="Playback rate (Hz)")
    args = parser.parse_args()

    try:
        main(**vars(args))
    except KeyboardInterrupt:
        pass
