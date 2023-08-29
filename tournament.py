#!/usr/bin/env python3

# Copyright 2023 Nobleo Technology B.V.
#
# SPDX-License-Identifier: Apache-2.0

import csv
from argparse import ArgumentParser
from itertools import combinations
from tempfile import NamedTemporaryFile

import pandas

from snakes.bots import bots
from snakes.game import Game, RoundType


def main(games):
    # write to a temporary file so that we have partial scores in case of a crash
    with NamedTemporaryFile('w+', suffix='.csv', delete=False) as f:
        print(f'writing game results to {f.name}')
        writer = csv.writer(f)
        # write bot names
        names = (Bot(id=i, grid_size=(1, 1)).name for i, Bot in enumerate(bots))
        writer.writerow(names)
        writer = csv.DictWriter(f, fieldnames=range(len(bots)))

        for _ in range(games):
            for a, b in combinations(range(len(bots)), r=2):
                agents = {a: bots[a], b: bots[b]}
                results = single_game(agents)
                writer.writerow(results)

        f.seek(0)
        df = pandas.read_csv(f)
        print(df)
        print(f'\ngame were written to {f.name}')


def single_game(agents):
    print()
    game = Game(agents=agents, round_type=RoundType.TURNS)
    while True:
        game.update()
        if game.finished():
            break
    print()
    print(f'{"Id":4}{"Name":20} Final position')
    ranking = game.rank()
    for id, rank in ranking.items():
        print(f'{id:<4}{game.agents[id].name:20} {rank}')
    print()
    return ranking


if __name__ == '__main__':
    parser = ArgumentParser(description='Nobleo Snakes')
    parser.add_argument('-g', '--games', default=10, type=int, help="Number of games to play")
    args = parser.parse_args()

    try:
        main(**vars(args))
    except KeyboardInterrupt:
        pass
