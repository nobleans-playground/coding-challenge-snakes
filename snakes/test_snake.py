# Copyright 2023 Nobleo Technology B.V.
#
# SPDX-License-Identifier: Apache-2.0

import numpy as np

from .constants import UP, RIGHT
from .snake import Snake


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
