from copy import deepcopy
from enum import Enum, auto
from math import floor
from random import sample
from traceback import print_exception
from typing import List, Tuple, Type, Dict

import numpy as np

from .constants import MOVE_VALUE_TO_DIRECTION, Move
from .snake import Snake


class RoundType(Enum):
    SIMULTANEOUS = auto()
    TURNS = auto()


def calculate_final_score(length, rank):
    multiplier = 1 / rank
    return floor(length * 2 * multiplier)


class Game:
    def __init__(self, agents: Dict[int, Type],
                 grid_size: Tuple[int, int] = (16, 16),
                 round_type: RoundType = RoundType.TURNS,
                 snakes: List[Snake] = None,
                 candies: List[np.array] = None):
        assert isinstance(agents, dict)
        assert isinstance(grid_size, Tuple)
        self.grid_size = grid_size
        self.agents = {i: Agent(id=i, grid_size=grid_size) for i, Agent in agents.items()}
        self.round_type = round_type
        self.turn = 0  # when rount_type == TURN, remember which agent was going to move
        self.snakes = snakes  # snake.id refers to an agent.id
        self.candies = candies
        self.scores = {}  # map from snake.id to score

        if snakes is None:
            self.snakes = []
            self.spawn_snakes(self.agents)
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
        starting_length = 2  # should be > 1 to prevent snakes from going backwards
        for i, index in zip(agents.keys(), starting_indices):
            x, y = divmod(index, self.grid_size[1])
            assert 0 <= x < self.grid_size[0]
            assert 0 <= y < self.grid_size[1]
            self.snakes.append(Snake(agents[i].id, np.tile([(x, y)], (starting_length, 1))))

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
                move_value = self._get_agents_move(snake)
                moves.append((snake, move_value))

            self._do_moves(moves)

        elif self.round_type == RoundType.TURNS:

            snake = next(s for s in self.snakes if s.id == self.turn)
            move_value = self._get_agents_move(snake)
            self._do_moves([(snake, move_value)])

            while True:
                # increment turn
                self.turn = (self.turn + 1) % len(self.agents)
                snake_id = list(self.agents.keys())[self.turn]
                # skip agents that are dead
                if len([True for s in self.snakes if s.id == snake_id]):
                    break

    def _get_agents_move(self, snake):
        snake = deepcopy(snake)
        other_snakes = [deepcopy(s) for s in self.snakes if s.id != snake.id]
        try:
            return self.agents[snake.id].determine_next_move(snake=snake, other_snakes=other_snakes,
                                                             candies=deepcopy(self.candies))
        except Exception as e:
            return e

    def _do_moves(self, moves: List[Tuple[Snake, Move]]):
        # first, move the snakes and record which candies have been eaten
        remove_candies = set()
        for snake, move_value in moves:
            if not isinstance(move_value, Move):
                continue  # skip bots that did an invalid move
            move = MOVE_VALUE_TO_DIRECTION[move_value]
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
        candy_indices = sample(sorted(free_indices), k=len(remove_candies))
        for index in candy_indices:
            x, y = divmod(index, self.grid_size[1])
            assert 0 <= x < self.grid_size[0]
            assert 0 <= y < self.grid_size[1]
            self.candies.append(np.array([x, y]))

        # figure out which snakes died
        dead = []
        for snake, move_value in moves:  # we only need to check the snakes that have moved
            if not isinstance(move_value, Move):
                if isinstance(move_value, Exception):
                    print(f'agent {snake.id} did not return an instance of Move, it returned an exception:')
                    print_exception(type(move_value), move_value, move_value.__traceback__)
                else:
                    print(f'agent {snake.id} did not return an instance of Move, it returned a {move_value!r}')
                dead.append(snake)
                continue
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

        rank = len(self.snakes) - len(dead) + 1
        for snake in dead:
            score = calculate_final_score(len(snake), rank)
            bonus = score - len(snake)
            print(f'snake {snake.id} died in {rank} place got {bonus} bonus points for a final score of {score}')
            self.scores[snake.id] = score

        for snake in dead:
            self.snakes.remove(snake)

        if len(self.snakes) <= 1:
            for snake in self.snakes:
                rank = 1
                score = calculate_final_score(len(snake), rank)
                bonus = score - len(snake)
                print(f'snake {snake.id} survived and got {bonus} bonus points for a final score of {score}')
                self.scores[snake.id] = score

    def possible_scores(self):
        """
        Return for each agent the score with the lowest possible bonus added
        :return: Tuple of score, agent_id
        """
        possible_scores = []  # type: List[Tuple[int, int]]
        for i in self.agents:
            if i in self.scores:
                possible_scores.append((self.scores[i], i))
            else:
                snake = next(s for s in self.snakes if s.id == i)
                lowest_rank = len(self.snakes)
                score = calculate_final_score(len(snake), lowest_rank)
                possible_scores.append((score, i))
        possible_scores.sort(reverse=True)
        return possible_scores

    def rank(self):
        possible_scores = self.possible_scores()

        rank = 1
        ranking = {}
        previous_score = possible_scores[0][0]
        for score, i in possible_scores:
            if score != previous_score:
                rank += 1
            ranking[i] = rank
        return ranking

    def finished(self):
        return len(self.snakes) <= 1
