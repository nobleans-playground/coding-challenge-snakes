import random

import numpy as np

from .bots import Random
from .constants import UP, RIGHT
from .game import Game, RoundType, Snake


def test_snake_sequence():
    head = np.array([5, 6])
    snake = Snake(0, np.array([head, head + UP, head + UP + RIGHT]))
    assert len(snake) == 3
    assert np.array_equal(snake[0], [5, 6])
    assert np.array_equal(snake[1], [5, 7])
    assert np.array_equal(snake[2], [6, 7])


def test_snake_grow():
    head = np.array([5, 6])
    snake = Snake(0, np.array([head]))
    snake.move(UP)
    assert len(snake) == 1
    assert np.array_equal(snake[0], [5, 7])

    snake.move(UP, grow=True)
    assert len(snake) == 2
    assert np.array_equal(snake[0], [5, 8])
    assert np.array_equal(snake[1], [5, 7])

    snake.move(UP)
    assert len(snake) == 2
    assert np.array_equal(snake[0], [5, 9])
    assert np.array_equal(snake[1], [5, 8])


def test_snake_collide():
    head = np.array([5, 6])
    snake = Snake(0, np.array([[5, 6], [5, 7], [6, 7]]))
    assert snake.collides(np.array([5, 6]))
    assert snake.collides(np.array([5, 7]))
    assert snake.collides(np.array([6, 7]))
    assert not snake.collides(np.array([6, 6]))


def test_game_snake_dies():
    random.seed(1)
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
    game.update()
    assert not game.finished()
    game.update()
    assert game.finished()
    assert game.scores[0] == 2  # snake 0 dies, so second place
    assert game.scores[1] == 1


def test_game_snake_eats():
    grid_size = (3, 3)
    """
    |0    |
    |0 *  |
    |  1 1|
    """
    snakes = [Snake(id=0, positions=np.array([
        [0, 1],
        [0, 2],
    ])), Snake(id=1, positions=np.array([
        [2, 0],
        [1, 0],
    ]))]
    candies = [np.array([1, 1])]
    game = Game(grid_size=grid_size, agents={0: Random, 1: Random}, round_type=RoundType.SIMULTANEOUS, snakes=snakes,
                candies=candies)
    assert not game.finished()
    game.update()
    assert not game.finished()
    assert (len(game.snakes[0]) == 3)
    assert (len(game.snakes[1]) == 2)
