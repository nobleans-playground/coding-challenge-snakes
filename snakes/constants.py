# Copyright 2023 Nobleo Technology B.V.
#
# SPDX-License-Identifier: Apache-2.0

from enum import auto, IntEnum, Enum

import numpy as np

UP = np.array([0, 1])
DOWN = np.array([0, -1])
LEFT = np.array([-1, 0])
RIGHT = np.array([1, 0])


class Move(IntEnum):
    UP = auto()
    DOWN = auto()
    LEFT = auto()
    RIGHT = auto()
    __str__ = Enum.__str__


MOVES = (Move.UP, Move.DOWN, Move.LEFT, Move.RIGHT)

MOVE_VALUE_TO_DIRECTION = {
    Move.UP: UP,
    Move.DOWN: DOWN,
    Move.LEFT: LEFT,
    Move.RIGHT: RIGHT,
}

MAX_TURNS = 10000
