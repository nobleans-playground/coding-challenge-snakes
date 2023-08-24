from abc import abstractmethod, ABC
from typing import List

import numpy as np

from .constants import Move
from .snake import Snake


class Bot(ABC):
    """
    To implement a Bot, you'll have to inherit from this class and implement all abstract methods
    """

    def __init__(self, id, grid_size):
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

    @abstractmethod
    def determine_next_move(self, snakes: List[Snake], candies: List[np.array]) -> Move:
        """
        When your snake is about to move, this method is called. Please return a Move

        :param snakes: All snakes on the field, including yours
        :param candies: All candies on the field
        :return: The move you want to make
        """
        pass
