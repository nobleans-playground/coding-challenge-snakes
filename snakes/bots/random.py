from random import choice

import numpy as np

from ..bot import Bot
from ..constants import Move, MOVE_VALUE_TO_DIRECTION


def is_on_grid(pos, grid_size):
    return 0 <= pos[0] < grid_size[0] and 0 <= pos[1] < grid_size[1]


def collides(head, snakes):
    for snake in snakes:
        for segment in snake:
            if np.array_equal(head, segment):
                return True
    return False


class Random(Bot):
    """
    Pick a random move, given that it is collision free
    """

    @property
    def name(self):
        return 'Random'

    def determine_next_move(self, snakes, candies) -> Move:
        snake = next(s for s in snakes if s.id == self.id)
        collision_free = [move for move, direction in MOVE_VALUE_TO_DIRECTION.items()
                          if is_on_grid(snake[0] + direction, self.grid_size)
                          and not collides(snake[0] + direction, snakes)]
        if collision_free:
            return choice(collision_free)
        else:
            return choice(list(Move))
