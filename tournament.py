#!/usr/bin/env python3

# Copyright 2023 Nobleo Technology B.V.
#
# SPDX-License-Identifier: Apache-2.0

import csv
from argparse import ArgumentParser
from itertools import combinations
from tempfile import NamedTemporaryFile

import numpy as np
import pandas

from snakes.bots import bots
from snakes.elo import print_tournament_summary
from snakes.game import Game, RoundType
from snakes.utils import levenshtein_ratio


def main(games, benchmark):
    # write to a temporary file so that we have partial scores in case of a crash
    with NamedTemporaryFile('w+', suffix='.csv', delete=False) as f:
        print(f'writing game results to {f.name}')
        writer = csv.writer(f)
        # write bot names
        names = [Bot(id=i, grid_size=(1, 1)).name for i, Bot in enumerate(bots)]
        writer.writerow(names + ['turns'] + ['cpu_' + name for name in names])
        fieldnames = list(range(len(bots))) + ['turns'] + ['cpu_' + name for name in names]
        writer = csv.DictWriter(f, fieldnames=fieldnames)

        if benchmark:
            names = [Bot(id=i, grid_size=(1, 1)).name for i, Bot in enumerate(bots)]
            name_matches = [levenshtein_ratio(name, benchmark) for name in names]
            a = np.argmax(name_matches)

        n = 1
        if benchmark:
            number_of_games = games * (len(bots) - 1)
            for _ in range(games):
                for b in range(len(bots)):
                    if a == b:
                        continue  # skip games against itself
                    agents = {a: bots[a], b: bots[b]}
                    row = single_game(agents)
                    writer.writerow(row)
                    f.flush()

                    print(f'Progress: {100 * n / number_of_games:.1f}% [{n} / {number_of_games}]')
                    n += 1
        else:
            number_of_games = games * len(bots) * (len(bots) - 1) // 2
            for _ in range(games):
                for a, b in combinations(range(len(bots)), r=2):
                    agents = {a: bots[a], b: bots[b]}
                    row = single_game(agents)
                    writer.writerow(row)
                    f.flush()

                    print(f'Progress: {100 * n / number_of_games:.1f}% [{n} / {number_of_games}]')
                    n += 1

        f.seek(0)
        df = pandas.read_csv(f)
        print(f'\ngame were written to {f.name}')
        print()
        print_tournament_summary(df)


def single_game(agents):
    names = [Bot(id=0, grid_size=(1, 1)).name for Bot in agents.values()]
    print()
    print('Battle:', ' vs '.join(names))
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

    row = ranking
    row['turns'] = game.turns
    row.update({'cpu_' + game.agents[i].name: cpu for i, cpu in game.cpu.items()})
    return row


if __name__ == '__main__':
    parser = ArgumentParser(description='Nobleo Snakes')
    parser.add_argument('-g', '--games', default=10, type=int, help="Number of games to play")
    parser.add_argument('-b', '--benchmark', metavar='SNAKE', help='Benchmark 1 agent against all others')
    args = parser.parse_args()

    try:
        main(**vars(args))
    except KeyboardInterrupt:
        pass
