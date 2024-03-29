# Copyright 2023 Nobleo Technology B.V.
#
# SPDX-License-Identifier: Apache-2.0

from abc import abstractmethod, ABC
from typing import List, Tuple

import numpy as np

from .constants import Move
from .snake import Snake


class Bot(ABC):
    """
    To implement a Bot, you'll have to inherit from this class and implement all abstract methods
    """

    def __init__(self, id: int, grid_size: Tuple[int, int]):
        """
        On initialization, this method is called. Please remember your id to find your snake on the field

        :param id: Your `snake.id == id`
        :param grid_size: The current grid size (x, y)
        """
        self.id = id
        self.grid_size = grid_size

    @property
    @abstractmethod
    def name(self):
        """
        The name you want to give your snake
        """
        pass

    @property
    @abstractmethod
    def contributor(self):
        """
        Your own name
        """
        pass

    @abstractmethod
    def determine_next_move(self, snake: Snake, other_snakes: List[Snake], candies: List[np.array]) -> Move:
        """
        When your snake is about to move, this method is called. Please return a Move

        :param snakes: Your own snake
        :param other_snakes: All other snakes that are alive on the field
        :param candies: All candies on the field
        :return: The move you want to make
        """
        pass
