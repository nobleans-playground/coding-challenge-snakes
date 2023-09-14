#!/usr/bin/env python3

# Copyright 2023 Nobleo Technology B.V.
#
# SPDX-License-Identifier: Apache-2.0

import random
import sys
from argparse import ArgumentParser
from math import isinf
from time import sleep

import numpy as np

from snakes.bots import bots
from snakes.game import Game, RoundType
from snakes.utils import levenshtein_ratio

numbers = ['⓪']


def fill_numbers():
    one = '①'.encode()
    for i in range(20):
        ba = bytearray(one)
        ba[2] += i
        numbers.append(bytes(ba).decode())


fill_numbers()


def number_to_circled(number: int) -> str:
    return numbers[number % len(numbers)]


class Printer:
    def print(self, game):
        grid = np.empty(game.grid_size, dtype=str)
        grid.fill(' ')
        for candy in game.candies:
            grid[candy[0], candy[1]] = '*'
        for snake in game.snakes:
            print(f'name={game.agents[snake.id].name!r} {snake}')
            for pos in snake:
                grid[pos[0], pos[1]] = number_to_circled(snake.id)

        print(f' {"▁" * 2 * game.grid_size[0]}▁ ')
        for j in reversed(range(grid.shape[1])):
            print('▕', end='')
            for i in range(grid.shape[0]):
                print(f' {grid[i, j]}', end='')
            print(' ▏')
        print(f' {"▔" * 2 * game.grid_size[0]}▔ ')


def main(snake1, snake2, rate, seed):
    names = [Bot(id=i, grid_size=(1, 1)).name for i, Bot in enumerate(bots)]

    name_matches = [levenshtein_ratio(name, snake1) for name in names]
    agent1 = np.argmax(name_matches)

    name_matches = [levenshtein_ratio(name, snake2) for name in names]
    agent2 = np.argmax(name_matches)

    # One agent could be up against itself, so we'll need to give new ids
    agents = {0: bots[agent1], 1: bots[agent2]}

    if seed is None:
        seed = random.randrange(sys.maxsize)
    random.seed(seed)

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

    print(f'For a replay of this game run the following command:\n./commandline.py {snake1!r} {snake2!r} --seed {seed}')
    print()
    print(f'{"Id":4}{"Name":20} Final position')
    for id, rank in game.rank().items():
        print(f'{id:<4}{game.agents[id].name:20} {rank}')


if __name__ == '__main__':
    parser = ArgumentParser(description='Battle two snakes in the command line')
    parser.add_argument('snake1', help="Name of snake 1")
    parser.add_argument('snake2', help="Name of snake 2")
    parser.add_argument('-r', '--rate', default=float('inf'), type=float, help="Playback rate (Hz)")
    parser.add_argument('-s', '--seed', type=int, help='Random seed')
    args = parser.parse_args()

    try:
        main(**vars(args))
    except KeyboardInterrupt:
        pass
