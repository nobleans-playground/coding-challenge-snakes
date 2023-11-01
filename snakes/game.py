# Copyright 2023 Nobleo Technology B.V.
#
# SPDX-License-Identifier: Apache-2.0
import re
from copy import deepcopy
from enum import Enum, auto
from io import StringIO
from math import floor
from random import sample
from time import time
from traceback import print_exception
from typing import List, Tuple, Type, Dict

import numpy as np

from .constants import MOVE_VALUE_TO_DIRECTION, Move, MAX_TURNS, MOVES
from .snake import Snake


class RoundType(Enum):
    SIMULTANEOUS = auto()
    TURNS = auto()


def calculate_final_score(length, rank):
    multiplier = 1 / rank
    return floor(length * 2 * multiplier)


class GameHistory:
    def __init__(self, grid_size, snakes, candies):
        self.grid_size = grid_size
        self.initial_candies = deepcopy(candies)
        self.initial_snakes = deepcopy(snakes)
        self.history = []

    def log_moves(self, moves: Dict[int, Move]):
        assert isinstance(moves, dict)
        self.history.append(moves)

    def log_candy_spawn(self, candy: Tuple[int, int]):
        assert isinstance(candy, tuple)
        self.history.append(candy)

    def serialize(self):
        io = StringIO()

        data = serialize(self.grid_size, self.initial_candies, 0, self.initial_snakes)
        io.write(data)

        for action in self.history:
            if isinstance(action, dict):
                for id, move in action.items():
                    io.write(f'{id}{"udlr"[MOVES.index(move)]}')
            if isinstance(action, Tuple):
                x, y = action
                io.write(f'c{x},{y}')
            io.write(' ')
        return io.getvalue()


class Game:
    def __init__(self, agents: Dict[int, Type],
                 grid_size: Tuple[int, int] = (16, 16),
                 round_type: RoundType = RoundType.TURNS,
                 snakes: List[Snake] = None,
                 candies: List[np.array] = None,
                 max_turns: int = MAX_TURNS):
        assert isinstance(agents, dict)
        assert isinstance(grid_size, Tuple)
        self.grid_size = grid_size
        self.agents = {}
        self.cpu = {i: 0 for i in agents}  # map from snake.id to CPU time
        for i, Agent in agents.items():
            start = time()
            self.agents[i] = Agent(id=i, grid_size=grid_size)
            self.cpu[i] += time() - start
        self.round_type = round_type
        self.turn = 0  # Index of the Agent which turn it is, only used when rount_type == TURN
        self.turns = 0  # Amount of turns that have passed
        self.snakes = snakes  # snake.id refers to an agent.id
        self.dead_snakes = []
        self.candies = candies
        self.max_turns = max_turns
        self.scores = {}  # map from snake.id to score

        if snakes is None:
            self.snakes = []
            self.spawn_snakes(self.agents)
        if candies is None:
            self.candies = []
            self.spawn_candies()
        assert isinstance(self.snakes, list)
        assert isinstance(self.candies, list)

        self.history = GameHistory(self.grid_size, self.snakes, self.candies)

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
            self.snakes.append(Snake(i, np.tile([(x, y)], (starting_length, 1))))

    def spawn_candies(self):
        indices = self.grid_size[0] * self.grid_size[1]
        percentage = 0.01
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

            self.turns += 1

        elif self.round_type == RoundType.TURNS:

            agent_id = list(self.agents)[self.turn]
            snake = next(s for s in self.snakes if s.id == agent_id)
            move_value = self._get_agents_move(snake)
            self._do_moves([(snake, move_value)])

            while True:
                # increment turn
                self.turn += 1
                if self.turn == len(self.agents):
                    self.turn = 0
                    self.turns += 1  # every player has had 1 turn
                snake_id = list(self.agents.keys())[self.turn]
                # skip agents that are dead
                if len([True for s in self.snakes if s.id == snake_id]):
                    break

        if self.turns >= self.max_turns:
            for snake in self.snakes:
                rank = 1
                score = calculate_final_score(len(snake), rank)
                bonus = score - len(snake)
                print(f'{self._snake_to_string(snake)} survived {self.turns} turns and got {bonus} bonus points for a '
                      f'final score of {score}')
                self.scores[snake.id] = score

    def _get_agents_move(self, snake):
        snake = deepcopy(snake)
        other_snakes = [deepcopy(s) for s in self.snakes if s.id != snake.id]
        start = time()
        try:
            move_value = self.agents[snake.id].determine_next_move(snake=snake, other_snakes=other_snakes,
                                                                   candies=deepcopy(self.candies))
        except Exception as e:
            move_value = e

        self.cpu[snake.id] += time() - start
        return move_value

    def _do_moves(self, moves: List[Tuple[Snake, Move]]):
        self.history.log_moves({snake.id: move for snake, move in moves})

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
            self.history.log_candy_spawn((x, y))

        # figure out which snakes died
        dead = []
        for snake, move_value in moves:  # we only need to check the snakes that have moved
            if not isinstance(move_value, Move):
                if isinstance(move_value, Exception):
                    print(
                        f'{self._snake_to_string(snake)} did not return an instance of Move, it returned an exception:')
                    print_exception(type(move_value), move_value, move_value.__traceback__)
                else:
                    print(
                        f'{self._snake_to_string(snake)} did not return an instance of Move, it returned a {move_value!r}')
                dead.append(snake)
                continue
            if not (0 <= snake[0][0] < self.grid_size[0] and 0 <= snake[0][1] < self.grid_size[1]):
                print(f'{self._snake_to_string(snake)} went out-of-bounds')
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
                        print(f'{self._snake_to_string(snake)} collided with itself')
                        dead.append(snake)
                        break
                elif other_snake.collides(snake[0]):
                    print(f'{self._snake_to_string(snake)} collided with snake {other_snake.id}')
                    dead.append(snake)
                    break

        rank = len(self.snakes) - len(dead) + 1
        for snake in dead:
            score = calculate_final_score(len(snake), rank)
            bonus = score - len(snake)
            print(
                f'{self._snake_to_string(snake)} died in {rank} place got {bonus} bonus points for a final score of {score}')
            self.scores[snake.id] = score

        for snake in dead:
            snake.dead = True
            self.dead_snakes.append(snake)
            self.snakes.remove(snake)

        if len(self.snakes) <= 1:
            for snake in self.snakes:
                rank = 1
                score = calculate_final_score(len(snake), rank)
                bonus = score - len(snake)
                print(
                    f'{self._snake_to_string(snake)} survived and got {bonus} bonus points for a final score of {score}')
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
        # if every snake has a score, the game is finished
        return len(self.scores) == len(self.agents)

    def _snake_to_string(self, snake: Snake) -> str:
        return f'{self.agents[snake.id].name} ({snake.id})'


def direction_to_move_value(direction):
    if direction[0] > 0:
        return Move.RIGHT
    elif direction[0] < 0:
        return Move.LEFT
    else:
        if direction[1] > 0:
            return Move.UP
        else:
            return Move.DOWN


def serialize(grid_size, candies, turn, snakes):
    data = f'{grid_size[0]}x{grid_size[1]}c'
    data += '/'.join(f'{candy[0]},{candy[1]}' for candy in candies)
    data += f't{turn}'

    snakedata = []
    for snake in snakes:
        snakestr = f'{snake[0][0]},{snake[0][1]}'
        for i in range(1, len(snake)):
            direction = snake[i] - snake[i - 1]
            move = direction_to_move_value(direction)
            snakestr += 'udlr'[MOVES.index(move)]
        snakedata.append(snakestr)
    data += 's'
    data += '/'.join(snakedata)

    return data


def deserialize(data: str):
    match = re.fullmatch(r'([^c]*)c([^s]*)t(\d+)s(.*)', data)
    grid_size = match.group(1)
    candies = match.group(2)
    turn = match.group(3)
    snakesstr = match.group(4)

    grid_size = tuple(int(x) for x in grid_size.split('x'))
    candies = [tuple(int(x) for x in c.split(',')) for c in candies.split('/')]
    turn = int(turn)

    snakes = []
    for id, snake in enumerate(snakesstr.split('/')):
        m = re.fullmatch('(\d+),(\d+)(\w+)', snake)
        segment = np.array([int(m.group(1)), int(m.group(2))])
        segments = [segment]
        for s in m.group(3):
            direction = MOVES['udlr'.index(s)]
            segment = segment + MOVE_VALUE_TO_DIRECTION[direction]
            segments.append(segment)
        snakes.append(Snake(id=id, positions=np.array(segments)))

    return grid_size, candies, turn, snakes
