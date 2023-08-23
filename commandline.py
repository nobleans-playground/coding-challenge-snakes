#!/usr/bin/env python3
from argparse import ArgumentParser
from math import isinf
from time import sleep

import numpy as np

from snakes.bots import bots
from snakes.game import Game, RoundType


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
    grid_size = (16, 8)
    agents = {i: Bot(id=i, grid_size=grid_size) for i, Bot in enumerate(bots)}

    name_matches = {i: levenshtein_ratio(agent.name, snake1) for i, agent in agents.items()}
    agent1 = max(name_matches.items(), key=lambda name_match: name_match[1])[0]

    name_matches = {i: levenshtein_ratio(agent.name, snake2) for i, agent in agents.items()}
    agent2 = max(name_matches.items(), key=lambda name_match: name_match[1])[0]

    agents = {i: agent for i, agent in agents.items() if i == agent1 or i == agent2}

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


def levenshtein_distance(s1: str, s2: str):
    assert isinstance(s1, str)
    assert isinstance(s2, str)
    s1 = s1.lower()
    s2 = s2.lower()

    if len(s1) < len(s2):
        return levenshtein_distance(s2, s1)

    if len(s2) == 0:
        return len(s1)

    previous_row = range(len(s2) + 1)
    for i, c1 in enumerate(s1):
        current_row = [i + 1]
        for j, c2 in enumerate(s2):
            insertions = previous_row[j + 1] + 1
            deletions = current_row[j] + 1
            substitutions = previous_row[j] + (c1 != c2)
            current_row.append(min(insertions, deletions, substitutions))
        previous_row = current_row

    return previous_row[-1]


def levenshtein_ratio(s1, s2):
    distance = levenshtein_distance(s1, s2)
    max_length = max(len(s1), len(s2))
    ratio = 1 - (distance / max_length)
    return ratio


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
