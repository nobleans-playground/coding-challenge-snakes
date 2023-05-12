from collections.abc import Sequence
from copy import deepcopy
from random import sample
from typing import List

import numpy as np

from bots import Bot, Move
from constants import MOVE_VALUE_TO_DIRECTION


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

    def collides(self, pos):
        for p in self.positions:
            if np.array_equal(p, pos):
                return True
        return False


class Game:
    def __init__(self, grid_size, agents: List[Bot], snakes: List[Snake] = None, candies: List[np.array] = None):
        assert isinstance(agents, dict)
        self.grid_size = grid_size
        self.agents = agents
        self.snakes = snakes  # snake.id refers to an agent.id
        self.candies = candies
        self.scores = {}  # map from snake.id to score

        if snakes is None:
            self.snakes = []
            self.spawn_snakes(agents)
        if candies is None:
            self.candies = []
            self.spawn_candies()
        assert isinstance(self.snakes, list)
        assert isinstance(self.candies, list)

        # check snake.id refers to an agent
        for snake in self.snakes:
            assert snake.id in self.agents
        # check that snake ids are unique
        snake_ids = [snake.id for snake in self.snakes]
        assert len(snake_ids) == len(set(snake_ids))

    def spawn_snakes(self, agents):
        starting_indices = sample(range(self.grid_size[0] * self.grid_size[1]), k=len(agents))
        for i, index in zip(agents.keys(), starting_indices):
            x, y = divmod(index, self.grid_size[1])
            assert 0 <= x < self.grid_size[0]
            assert 0 <= y < self.grid_size[1]
            self.snakes.append(Snake(agents[i].id, np.array([(x, y)])))

    def spawn_candies(self):
        indices = self.grid_size[0] * self.grid_size[1]
        percentage = 0.1
        candy_indices = sample(range(indices), k=round(percentage * indices))
        for index in candy_indices:
            x, y = divmod(index, self.grid_size[1])
            assert 0 <= x < self.grid_size[0]
            assert 0 <= y < self.grid_size[1]
            self.candies.append(np.array([x, y]))

    def update(self):
        moves = {}
        for snake in self.snakes:
            move_value = self.agents[snake.id].determine_next_move(snakes=deepcopy(self.snakes),
                                                                   candies=deepcopy(self.candies))
            if not isinstance(move_value, Move):
                raise TypeError(f'agent {snake.id} did not return a Move, it returned a {move_value}')
            moves[snake.id] = MOVE_VALUE_TO_DIRECTION[move_value]

        remove_candies = []
        for snake in self.snakes:
            move = moves[snake.id]
            for i, candy in enumerate(self.candies):
                if np.array_equal(snake[0] + move, candy):
                    remove_candies.append(i)
                    snake.move(move, grow=True)
                    break
            else:
                snake.move(move)
        self.candies = [i for j, i in enumerate(self.candies) if j not in remove_candies]

        dead = []
        for snake in self.snakes:
            if not (0 <= snake[0][0] < self.grid_size[0] and 0 <= snake[0][1] < self.grid_size[1]):
                print(f'snake {snake.id} went out-of-bounds')
                dead.append(snake)
                continue

            for other_snake in self.snakes:
                if snake == other_snake:
                    self_collision = False
                    # self collision, don't check head
                    for p in snake[1:]:
                        if np.array_equal(p, snake[0]):
                            self_collision = True
                            break
                    if self_collision:
                        print(f'snake {snake.id} collided with itself')
                        dead.append(snake)
                        break
                elif other_snake.collides(snake[0]):
                    print(f'snake {snake.id} collided with snake {other_snake.id}')
                    dead.append(snake)
                    break

        for snake in dead:
            self.snakes.remove(snake)
        rank = len(self.snakes) + 1
        for snake in dead:
            print(f'snake {snake.id} died and got the {rank} place')
            self.scores[snake.id] = rank

        if len(self.snakes) <= 1:
            for snake in self.snakes:
                self.scores[snake.id] = 1

    def finished(self):
        return len(self.snakes) <= 1

    def on_snake(self, pos):
        raise NotImplementedError()
