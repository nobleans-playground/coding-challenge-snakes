#!/usr/bin/env python3
from argparse import ArgumentParser

from bots import bots
from game import Game


def main(games):
    grid_size = (16, 8)
    agents = [Bot(id=i, grid_size=grid_size) for i, Bot in enumerate(bots)]
    game = Game(grid_size=grid_size, agents=agents)
    while True:
        game.update()
        if game.finished():
            break

    print('Name\tFinal position')
    for id, score in game.scores.items():
        print(f'{game.agents[id].name}\t{score}')


if __name__ == '__main__':
    parser = ArgumentParser(description='Nobleo Snakes')
    parser.add_argument('-g', '--games', default=10, type=int, help="Number of games to play")
    args = parser.parse_args()

    try:
        main(**vars(args))
    except KeyboardInterrupt:
        pass
