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
import pandas as pd

from snakes.bots import bots
from snakes.elo import print_tournament_summary
from snakes.game import Game, RoundType, serialize, deserialize
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
            for pos in snake:
                grid[pos[0], pos[1]] = number_to_circled(snake.id)

        print(f' {"▁" * 2 * game.grid_size[0]}▁ ')
        for j in reversed(range(grid.shape[1])):
            print('▕', end='')
            for i in range(grid.shape[0]):
                print(f' {grid[i, j]}', end='')
            print(' ▏')
        print(f' {"▔" * 2 * game.grid_size[0]}▔ ')
        print('Game state:', serialize(game.grid_size, game.candies, game.turn, game.snakes))


def main(snake1, snake2, rate, seed, start):
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

    if start:
        grid_size, candies, turn, snakes = deserialize(start)
        game.grid_size = grid_size
        game.candies = candies
        game.turn = turn
        game.snakes = snakes

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
    row = {game.agents[id].name: rank for id, rank in game.rank().items()}
    row['turns'] = game.turns
    row['seed'] = seed
    row.update({'cpu_' + game.agents[i].name: cpu for i, cpu in game.cpu.items()})
    df = pd.DataFrame([row])
    print_tournament_summary(df, elo=False)


if __name__ == '__main__':
    parser = ArgumentParser(description='Battle two snakes in the command line')
    parser.add_argument('snake1', help="Name of snake 1")
    parser.add_argument('snake2', help="Name of snake 2")
    parser.add_argument('-r', '--rate', default=float('inf'), type=float, help="Playback rate (Hz)")
    parser.add_argument('-s', '--seed', type=int, help='Random seed')
    parser.add_argument('--start', help='Start from game state')
    args = parser.parse_args()

    try:
        main(**vars(args))
    except KeyboardInterrupt:
        pass
