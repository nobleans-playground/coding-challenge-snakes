# Copyright 2023 Nobleo Technology B.V.
#
# SPDX-License-Identifier: Apache-2.0

import numpy as np

from .bot import Bot
from .bots.random import Random
from .game import Game, RoundType, serialize, deserialize
from .snake import Snake


def test_game_snake_dies():
    """
    A grid where one of the snakes can move only 1 tile, while the other can move multiple times. Snake 1 will win.
    """
    grid_size = (3, 3)
    """
    |  0 1|
    |0 0 1|
    |0 0  |
    """
    snakes = [Snake(id=0, positions=np.array([
        [1, 2],
        [1, 1],
        [0, 1],
        [0, 0],
        [1, 0],
    ])), Snake(id=1, positions=np.array([
        [2, 1],
        [2, 2],
    ]))]
    game = Game(grid_size=grid_size, agents={0: Random, 1: Random}, round_type=RoundType.SIMULTANEOUS, snakes=snakes,
                candies=[])
    assert not game.finished()
    list(game.update())
    assert not game.finished()
    list(game.update())
    assert game.finished()

    # snake 0 dies, so its got second place
    # however due to the current bonus structure, the longer snake wins
    ranking = game.rank()
    assert ranking[0] == 1
    assert ranking[1] == 2


def test_game_snake_eats():
    grid_size = (3, 3)
    """
    |0 1  |
    |0 1  |
    |*    |
    """
    snakes = [Snake(id=0, positions=np.array([
        [0, 1],
        [0, 2],
    ])), Snake(id=1, positions=np.array([
        [1, 1],
        [1, 2],
    ]))]
    candies = [np.array([0, 0])]
    game = Game(grid_size=grid_size, agents={0: Random, 1: Random}, round_type=RoundType.SIMULTANEOUS, snakes=snakes,
                candies=candies)
    assert not game.finished()
    list(game.update())
    assert not game.finished()
    assert (len(game.snakes[0]) == 3)
    assert (len(game.snakes[1]) == 2)


class BotThatThrows(Bot):
    @property
    def name(self):
        return 'Random'

    @property
    def contributor(self):
        return 'Nobleo'

    def determine_next_move(self, snake, other_snakes, candies):
        raise NotImplementedError()


def test_game_snake_throws():
    """
    A grid where one of the snakes can move only 1 tile, while the other can move multiple times. Snake 1 will win.
    """
    grid_size = (3, 3)
    """
    |    1|
    |0   1|
    |0    |
    """
    snakes = [Snake(id=0, positions=np.array([
        [0, 0],
        [0, 1],
    ])), Snake(id=1, positions=np.array([
        [2, 2],
        [2, 1],
    ]))]
    game = Game(grid_size=grid_size, agents={0: BotThatThrows, 1: Random}, round_type=RoundType.SIMULTANEOUS,
                snakes=snakes,
                candies=[])
    assert not game.finished()
    list(game.update())
    assert game.finished()
    ranking = game.rank()
    assert ranking[0] == 2  # snake 0 dies, so second place
    assert ranking[1] == 1


def test_game_snake_returns_invalid_move():
    class BotThatThrows(Bot):
        @property
        def name(self):
            return 'Random'

        @property
        def contributor(self):
            return 'Nobleo'

        def determine_next_move(self, snake, other_snakes, candies):
            return 'INVALID_MOVE'

    """
    A grid where one of the snakes can move only 1 tile, while the other can move multiple times. Snake 1 will win.
    """
    grid_size = (3, 3)
    """
    |    1|
    |0   1|
    |0    |
    """
    snakes = [Snake(id=0, positions=np.array([
        [0, 0],
        [0, 1],
    ])), Snake(id=1, positions=np.array([
        [2, 2],
        [2, 1],
    ]))]
    game = Game(grid_size=grid_size, agents={0: BotThatThrows, 1: Random}, round_type=RoundType.SIMULTANEOUS,
                snakes=snakes,
                candies=[])
    assert not game.finished()
    list(game.update())
    assert game.finished()
    ranking = game.rank()
    assert ranking[0] == 2  # snake 0 dies, so second place
    assert ranking[1] == 1


def test_game_ranking():
    grid_size = (100, 100)
    snakes = [Snake(id=i, positions=np.tile([[i, i]], (10, 1))) for i in range(5)]
    agents = {i: BotThatThrows for i in range(len(snakes))}
    game = Game(grid_size=grid_size, agents=agents, round_type=RoundType.TURNS, snakes=snakes, candies=[])

    while not game.finished():
        list(game.update())

    ranking = game.rank()
    assert ranking[0] == 5
    assert ranking[1] == 4
    assert ranking[2] == 3
    assert ranking[3] == 2
    assert ranking[4] == 1
    print(game.scores)


def test_game_deserialize():
    data = '16x16c13,1/14,2/0,10t0s0,9rruuurrrdld/6,14drddddrrdlldd'
    grid_size, candies, turn, snakes = deserialize(data)
    assert data == serialize(grid_size, candies, turn, snakes)
