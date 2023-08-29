# Copyright 2023 Nobleo Technology B.V.
#
# SPDX-License-Identifier: Apache-2.0

from random import choice
from typing import List

import numpy as np

from ..bot import Bot
from ..constants import Move, MOVE_VALUE_TO_DIRECTION
from ..snake import Snake


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

    @property
    def contributor(self):
        return 'Nobleo'

    def determine_next_move(self, snake: Snake, other_snakes: List[Snake], candies: List[np.array]) -> Move:
        all_snakes = [snake] + other_snakes
        collision_free = [move for move, direction in MOVE_VALUE_TO_DIRECTION.items()
                          if is_on_grid(snake[0] + direction, self.grid_size)
                          and not collides(snake[0] + direction, all_snakes)]
        if collision_free:
            return choice(collision_free)
        else:
            return choice(list(Move))
