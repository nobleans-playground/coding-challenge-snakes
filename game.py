from collections.abc import Sequence
from random import choices
from typing import List

import numpy as np

from bots import Bot, Move

UP = np.array([0, 1])
DOWN = np.array([0, -1])
LEFT = np.array([-1, 0])
RIGHT = np.array([1, 0])
MOVES = (Move.UP, Move.DOWN, Move.LEFT, Move.RIGHT)

MOVE_VALUE_TO_DIRECTION = {
    Move.UP: UP,
    Move.DOWN: DOWN,
    Move.LEFT: LEFT,
    Move.RIGHT: RIGHT,
}


class Snake(Sequence):
    def __init__(self, id, positions):
        assert len(positions.shape) == 2
        assert positions.shape[1] == 2
        self.id = id
        self.positions = positions

    def move(self, move, grow=False):
        if grow:
            self.positions = np.concatenate((self.positions[0:1] + move, self.positions))
        else:
            head = self.positions[0]
            self.positions = np.roll(self.positions, 1, axis=0)
            self.positions[0] = head + move

    def __iter__(self):
        return iter(self.positions)

    def __len__(self):
        return self.positions.shape[0]

    def __getitem__(self, i):
        return self.positions[i]

    def __repr__(self):
        return f'id={self.id} positions={self.positions.tolist()}'


class Game:
    def __init__(self, grid_size, agents: List[Bot]):
        self.grid_size = grid_size
        self.agents = agents

        starting_indices = choices(range(self.grid_size[0] * self.grid_size[1]), k=len(agents))
        self.snakes = []
        for i, index in enumerate(starting_indices):
            x, y = divmod(index, self.grid_size[0])
            assert 0 <= x < self.grid_size[0]
            assert 0 <= y < self.grid_size[1]
            self.snakes.append(Snake(i, np.array([(x, y)])))

    def update(self):
        moves = {}
        for snake in self.snakes:
            move_value = self.agents[snake.id].determine_next_move()
            if not isinstance(move_value, Move):
                raise TypeError(f'agent {snake.id} did not return a Move, it returned a {move_value}')
            moves[snake.id] = MOVE_VALUE_TO_DIRECTION[move_value]

        self.apply_moves(moves)

    def apply_moves(self, moves):
        for id, move in moves.items():
            self.snakes[id].move(move)
