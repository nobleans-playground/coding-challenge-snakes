from abc import ABC, abstractmethod
from random import choice
from typing import List

import numpy as np

from constants import Move, MOVE_VALUE_TO_DIRECTION


class Bot(ABC):
    def __init__(self, id, grid_size):
        self.id = id
        self.grid_size = grid_size

    @property
    @abstractmethod
    def name(self):
        pass

    @abstractmethod
    def determine_next_move(self, snakes, candies) -> Move:
        pass


def is_on_grid(pos, grid_size):
    return 0 <= pos[0] < grid_size[0] and 0 <= pos[1] < grid_size[1]


def collides(head, snakes):
    for snake in snakes:
        for segment in snake:
            if np.array_equal(head, segment):
                return True
    return False


class Random(Bot):
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


class SimpleEater(Bot):
    @property
    def name(self):
        return 'Simple Eater'

    def determine_next_move(self, snakes, candies) -> Move:
        snake = next(s for s in snakes if s.id == self.id)

        # highest priority, a move that is on the grid
        on_grid = [move for move in MOVE_VALUE_TO_DIRECTION
                   if is_on_grid(snake[0] + MOVE_VALUE_TO_DIRECTION[move], self.grid_size)]
        if not on_grid:
            return self.choose_towards_candy(list(Move), snake, candies)

        # then avoid collisions with other snakes
        collision_free = [move for move in on_grid
                          if is_on_grid(snake[0] + MOVE_VALUE_TO_DIRECTION[move], self.grid_size)
                          and not collides(snake[0] + MOVE_VALUE_TO_DIRECTION[move], snakes)]
        if not collision_free:
            return self.choose_towards_candy(on_grid, snake, candies)

        # then avoid the heads of other snakes
        avoids_snakes = [move
                         for move in collision_free
                         for other_snake in snakes
                         if other_snake is not snake
                         if np.linalg.norm((snake[0] + MOVE_VALUE_TO_DIRECTION[move]) - other_snake[0], 1) > 1]
        if not avoids_snakes:
            return self.choose_towards_candy(collision_free, snake, candies)

        return self.choose_towards_candy(avoids_snakes, snake, candies)

    def choose_towards_candy(self, moves: List[Move], snake, candies):
        if not candies:
            return choice(moves)
        return min(moves,
                   key=lambda move: self.distance_to_closest_candy(snake[0] + MOVE_VALUE_TO_DIRECTION[move], candies))

    def distance_to_closest_candy(self, position, candies):
        distances = [np.linalg.norm(position - candy, 1) for candy in candies]
        return min(distances)
