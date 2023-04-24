from enum import Enum, auto

import numpy as np

UP = np.array([0, 1])
DOWN = np.array([0, -1])
LEFT = np.array([-1, 0])
RIGHT = np.array([1, 0])


class Move(Enum):
    UP = auto()
    DOWN = auto()
    LEFT = auto()
    RIGHT = auto()


MOVES = (Move.UP, Move.DOWN, Move.LEFT, Move.RIGHT)

MOVE_VALUE_TO_DIRECTION = {
    Move.UP: UP,
    Move.DOWN: DOWN,
    Move.LEFT: LEFT,
    Move.RIGHT: RIGHT,
}
