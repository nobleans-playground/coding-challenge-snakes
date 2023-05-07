#!/usr/bin/env python3
import csv
from argparse import ArgumentParser
from tempfile import NamedTemporaryFile

import pandas

from bots import bots
from game import Game


def main(games):
    grid_size = (16, 8)
    # write to a temporary file so that we have partial scores in case of a crash
    with NamedTemporaryFile('w+', suffix='.csv', delete=False) as f:
        print(f'writing game results to {f.name}')
        writer = csv.writer(f)
        # write bot names
        writer.writerow(Bot(id=i, grid_size=grid_size).name for i, Bot in enumerate(bots))

        writer = csv.DictWriter(f, fieldnames=range(len(bots)))
        for _ in range(games):
            results = single_game(grid_size=grid_size)
            # writer.writerow([score for id, score in sorted(results.items())])
            writer.writerow(results)

        f.seek(0)
        df = pandas.read_csv(f)
        print(df)


def single_game(grid_size):
    print()
    agents = [Bot(id=i, grid_size=grid_size) for i, Bot in enumerate(bots)]
    game = Game(grid_size=grid_size, agents=agents)
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
