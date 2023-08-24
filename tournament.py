#!/usr/bin/env python3
import csv
from argparse import ArgumentParser
from itertools import combinations
from tempfile import NamedTemporaryFile

import pandas

from snakes.bots import bots
from snakes.game import Game, RoundType


def main(games):
    grid_size = (16, 8)
    round_robin(games, grid_size=grid_size)


def round_robin(games, grid_size):
    # write to a temporary file so that we have partial scores in case of a crash
    with NamedTemporaryFile('w+', suffix='.csv', delete=False) as f:
        print(f'writing game results to {f.name}')
        writer = csv.writer(f)
        # write bot names
        writer.writerow(Bot(id=i, grid_size=grid_size).name for i, Bot in enumerate(bots))
        writer = csv.DictWriter(f, fieldnames=range(len(bots)))

        for _ in range(games):
            for a, b in combinations(range(len(bots)), r=2):
                agents = {a: bots[a](id=a, grid_size=grid_size), b: bots[b](id=b, grid_size=grid_size)}
                results = single_game(grid_size, agents)
                writer.writerow(results)

        f.seek(0)
        df = pandas.read_csv(f)
        print(df)
        print(f'\ngame were written to {f.name}')


def single_game(grid_size, agents):
    print()
    game = Game(grid_size=grid_size, agents=agents, round_type=RoundType.TURNS)
    while True:
        game.update()
        if game.finished():
            break
    print()
    print(f'{"Name":20} Final position')
    for id, score in game.scores.items():
        print(f'{game.agents[id].name:20} {score}')
    print()
    return game.scores


if __name__ == '__main__':
    parser = ArgumentParser(description='Nobleo Snakes')
    parser.add_argument('-g', '--games', default=10, type=int, help="Number of games to play")
    args = parser.parse_args()

    try:
        main(**vars(args))
    except KeyboardInterrupt:
        pass
