from copy import deepcopy
from enum import Enum, auto
from random import sample
from typing import List, Tuple, Dict

import numpy as np

from bots import Bot
from constants import MOVE_VALUE_TO_DIRECTION, Move
from snake import Snake


class RoundType(Enum):
    SIMULTANEOUS = auto()
    TURNS = auto()


class Game:
    def __init__(self, grid_size, agents: Dict[int, Bot],
                 round_type: RoundType = RoundType.TURNS,
                 snakes: List[Snake] = None,
                 candies: List[np.array] = None):
        assert isinstance(agents, dict)
        self.grid_size = grid_size
        self.agents = agents
        self.round_type = round_type
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
        if self.round_type == RoundType.SIMULTANEOUS:

            moves: List[Tuple[Snake, Move]] = []
            for snake in self.snakes:
                move_value = self.agents[snake.id].determine_next_move(snakes=deepcopy(self.snakes),
                                                                       candies=deepcopy(self.candies))
                if not isinstance(move_value, Move):
                    raise TypeError(f'agent {snake.id} did not return a Move, it returned a {move_value}')
                moves.append((snake, MOVE_VALUE_TO_DIRECTION[move_value]))

            self._do_moves(moves)

        elif self.round_type == RoundType.TURNS:

            for snake in self.snakes:
                move_value = self.agents[snake.id].determine_next_move(snakes=deepcopy(self.snakes),
                                                                       candies=deepcopy(self.candies))
                if not isinstance(move_value, Move):
                    raise TypeError(f'agent {snake.id} did not return a Move, it returned a {move_value}')
                self._do_moves([(snake, MOVE_VALUE_TO_DIRECTION[move_value])])

    def _do_moves(self, moves):
        # first, move the snakes and record which candies have been eaten
        remove_candies = set()
        for snake, move in moves:
            for i, candy in enumerate(self.candies):
                if np.array_equal(snake[0] + move, candy):
                    remove_candies.add(i)
                    snake.move(move, grow=True)
                    break
            else:
                snake.move(move)
        self.candies = [i for j, i in enumerate(self.candies) if j not in remove_candies]

        # respawn new candies
        occupied_indices = {x * self.grid_size[1] + y for x, y in self.candies}
        free_indices = set(range(self.grid_size[0] * self.grid_size[1])) - occupied_indices
        candy_indices = sample(free_indices, k=len(remove_candies))
        for index in candy_indices:
            x, y = divmod(index, self.grid_size[1])
            assert 0 <= x < self.grid_size[0]
            assert 0 <= y < self.grid_size[1]
            self.candies.append(np.array([x, y]))

        # figure out which snakes died
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
