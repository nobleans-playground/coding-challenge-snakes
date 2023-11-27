# Copyright 2023 Nobleo Technology B.V.
#
# SPDX-License-Identifier: Apache-2.0
import re
from copy import deepcopy
from enum import Enum, auto
from math import floor
from pprint import pformat
from random import sample
from time import time
from traceback import print_exception
from typing import List, Tuple, Type, Dict, Iterator

import numpy as np

from .bot import Bot
from .constants import MOVE_VALUE_TO_DIRECTION, Move, MAX_TURNS, UP, DOWN, LEFT, RIGHT, MOVES
from .snake import Snake


class RoundType(Enum):
    SIMULTANEOUS = auto()
    TURNS = auto()


def calculate_final_score(length, rank):
    multiplier = 1 / rank
    return floor(length * 2 * multiplier)


class GameHistory:
    def __init__(self, grid_size, snakes, candies, history=None):
        self.grid_size = grid_size
        self.initial_candies = deepcopy(candies)
        self.initial_snakes = deepcopy(snakes)
        # History items can be:
        # - dict from snake index to move
        # - candy tuple
        self.history = history if history is not None else []  # type: List[dict[int,Move] | Tuple[int, int]]

    def log_moves(self, moves: List[Tuple[Snake, Move]]):
        assert isinstance(moves, List)
        logged_moves = {}
        for snake, move in moves:
            index = next(i for i, s in enumerate(self.initial_snakes) if s.id == snake.id)
            logged_moves[index] = move
        self.history.append(logged_moves)

    def log_candy_spawn(self, candy: Tuple[int, int]):
        assert isinstance(candy, tuple)
        self.history.append(candy)

    def serialize(self) -> Dict[str, str]:
        actions = []
        for action in self.history:
            if isinstance(action, dict):
                for id, move in action.items():
                    actions.append(f'{id}{move_to_str(move)}')
            if isinstance(action, Tuple):
                x, y = action
                actions.append(f'c{x},{y}')

        return {
            'initial': serialize(self.grid_size, self.initial_candies, 0, self.initial_snakes),
            'moves': " ".join(actions)
        }

    @staticmethod
    def deserialize(data):
        grid_size, candies, turn, snakes = deserialize(data['initial'])
        history = []
        for moves_string in data['moves'].split(' '):
            if moves_string.startswith('c'):
                candy = tuple(int(x) for x in moves_string[1:].split(','))
                history.append(candy)
            else:
                moves = {}
                for match in re.finditer(r'(\d+)([udlr])', moves_string):
                    id = int(match.group(1))
                    move = str_to_move(match.group(2))
                    moves[id] = move
                history.append(moves)
        return GameHistory(grid_size, snakes, candies, history)

    def __repr__(self):
        return f'{self.__class__.__name__}(grid_size={self.initial_snakes}, snakes={self.initial_snakes}, history={self.history})'


class GameEvent:
    pass


class InvalidMove(GameEvent):
    def __init__(self, snake: Snake, move_value):
        self.snake = snake
        self.move_value = move_value


class OutOfBounds(GameEvent):
    def __init__(self, snake: Snake):
        self.snake = snake


class Collision(GameEvent):
    def __init__(self, snake: Snake, other_snake: Snake):
        self.snake = snake
        self.other_snake = other_snake


class Death(GameEvent):
    def __init__(self, snake: Snake, rank, score):
        self.snake = snake
        self.rank = rank
        self.score = score


class Finished(GameEvent):
    def __init__(self, state):
        self.state = state


def snake_to_str(snake: Snake, agents: Dict[int, Bot]) -> str:
    assert isinstance(snake, Snake), snake
    assert isinstance(agents, dict), agents
    assert isinstance(agents[snake.id], str), agents
    return f'{agents[snake.id]} ({snake.id})'


def print_event(event: GameEvent, agents: Dict[int, str]):
    assert isinstance(event, GameEvent)
    assert isinstance(agents, dict), agents
    assert all(isinstance(a, str) for a in agents.values()), agents

    if isinstance(event, InvalidMove):
        if isinstance(event.move_value, Exception):
            print(f'{snake_to_str(event.snake, agents)} did not return an instance of Move, it returned an exception:')
            print_exception(type(event.move_value), event.move_value, event.move_value.__traceback__)
        else:
            print(f'{snake_to_str(event.snake, agents)} did not return an instance of Move, it returned a '
                  f'{event.move_value!r}')
    elif isinstance(event, OutOfBounds):
        print(f'{snake_to_str(event.snake, agents)} went out-of-bounds')
    elif isinstance(event, Collision):
        if event.snake == event.other_snake:
            print(f'{snake_to_str(event.snake, agents)} collided with itself')
        else:
            print(f'{snake_to_str(event.snake, agents)} collided with snake {snake_to_str(event.other_snake, agents)}')
    elif isinstance(event, Death):
        bonus = event.score - len(event.snake)
        print(f'{snake_to_str(event.snake, agents)} died in {event.rank} place got {bonus} bonus points for a final '
              f'score of {event.score}')
    elif isinstance(event, Finished):
        for snake in event.state.snakes:
            if snake is not None:
                score = event.state.scores[snake.id]
                bonus = score - len(snake)
                print(f'{snake_to_str(snake, agents)} survived {event.state.turns} turns and got {bonus} bonus points '
                      f'for a final score of {score}')
    else:
        assert False, "Unknown event type"


class State:
    def __init__(self,
                 snakes: List[Snake],
                 grid_size: Tuple[int, int] = (16, 16),
                 round_type: RoundType = RoundType.TURNS,
                 candies: List[np.array] = None,
                 max_turns: int = MAX_TURNS):
        assert isinstance(snakes, list)
        assert isinstance(grid_size, Tuple)
        self.snakes = snakes  # type: List[Snake | None] # All snakes in turn order, None if dead. snake.id refers to an agent.id.
        self.grid_size = grid_size
        self.round_type = round_type
        self.turn = 0  # Index of the snake which turn it is, only used when rount_type == TURN
        self.turns = 0  # Amount of turns that have passed
        self.dead_snakes = []
        self.candies = candies if candies is not None else []
        self.max_turns = max_turns
        self.scores = {}  # map from snake.id to score

        # Initial candy spawns are logged as move, so we don't need to include them to the history
        self.history = GameHistory(self.grid_size, self.snakes, self.candies)

        if candies is None:
            self.candies = []
            self.respawn_candies()
        assert isinstance(self.candies, list)

        # check that snake ids are unique
        snake_ids = [snake.id for snake in self.snakes]
        assert len(snake_ids) == len(set(snake_ids))

    def players_turn(self) -> Iterator[Snake]:
        """Return all players that should play a move in the next turn"""
        if self.round_type == RoundType.SIMULTANEOUS:
            yield from (s for s in self.snakes if s is not None)

        if self.round_type == RoundType.TURNS:
            assert self.snakes[self.turn] is not None
            yield self.snakes[self.turn]

    def do_moves(self, moves: List[Tuple[Snake, Move]]) -> Iterator[GameEvent]:
        if __debug__:
            should_move = set(self.players_turn())
            has_moves = set(s for s, _ in moves)
            assert should_move == has_moves, f'{should_move} == {has_moves}'
        self.history.log_moves(moves)

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

        # figure out which snakes died
        dead = []
        for snake, move_value in moves:  # we only need to check the snakes that have moved
            if not isinstance(move_value, Move):
                yield InvalidMove(snake, move_value)
                dead.append(snake)
                continue
            if not (0 <= snake[0][0] < self.grid_size[0] and 0 <= snake[0][1] < self.grid_size[1]):
                yield OutOfBounds(snake)
                dead.append(snake)
                continue

            for other_snake in self.snakes:
                if other_snake is None:
                    pass
                elif snake == other_snake:
                    self_collision = False
                    # self collision, don't check head
                    for p in snake[1:]:
                        if np.array_equal(p, snake[0]):
                            self_collision = True
                            break
                    if self_collision:
                        yield Collision(snake, snake)
                        dead.append(snake)
                        break
                elif other_snake.collides(snake[0]):
                    yield Collision(snake, other_snake)
                    dead.append(snake)
                    break

        for snake in dead:
            snake.dead = True
            self.dead_snakes.append(snake)
            self.snakes[self.snakes.index(snake)] = None

        rank = sum(1 for s in self.snakes if s is not None) + 1
        for snake in dead:
            score = calculate_final_score(len(snake), rank)
            yield Death(snake, rank, score)
            self.scores[snake.id] = score

        # increment the turn
        if self.round_type == RoundType.SIMULTANEOUS:
            self.turns += 1
        elif self.round_type == RoundType.TURNS:
            while True:
                # increment turn
                self.turn += 1
                if self.turn == len(self.snakes):
                    self.turn = 0
                    self.turns += 1  # every player has had 1 turn
                if self.snakes[self.turn] is not None:
                    break
                # otherwise, skip agents that are dead

        # check if the game has finished
        game_finished = sum(1 for s in self.snakes if s is not None) <= 1 or self.turns >= self.max_turns

        if game_finished:
            for snake in self.snakes:
                if snake is not None:
                    rank = 1
                    score = calculate_final_score(len(snake), rank)
                    self.scores[snake.id] = score
            yield Finished(self)

    def respawn_candies(self):
        # respawn new candies
        n_indices = self.grid_size[0] * self.grid_size[1]
        occupied_indices = {x * self.grid_size[1] + y for x, y in self.candies}
        free_indices = set(range(n_indices)) - occupied_indices
        percentage = 0.01
        candy_indices = sample(sorted(free_indices), k=round(percentage * n_indices) - len(self.candies))
        for index in candy_indices:
            x, y = divmod(index, self.grid_size[1])
            assert 0 <= x < self.grid_size[0]
            assert 0 <= y < self.grid_size[1]
            self.spawn_candy(x, y)

    def spawn_candy(self, x, y):
        self.candies.append(np.array([x, y]))
        self.history.log_candy_spawn((x, y))

    def __repr__(self):
        return f'{self.__class__.__name__}({pformat(self.__dict__, indent=2)})'


class Game:
    def __init__(self, agents: Dict[int, Type],
                 grid_size: Tuple[int, int] = (16, 16),
                 round_type: RoundType = RoundType.TURNS,
                 snakes: List[Snake] = None,
                 candies: List[np.array] = None,
                 max_turns: int = MAX_TURNS):

        assert isinstance(agents, dict)
        self.agents = {}
        self.cpu = {i: 0 for i in agents}  # map from snake.id to CPU time
        for i, Agent in agents.items():
            start = time()
            self.agents[i] = Agent(id=i, grid_size=grid_size)
            self.cpu[i] += time() - start

        if snakes is None:
            snakes = self.create_snakes(grid_size, self.agents.keys())
        self.state = State(grid_size=grid_size, round_type=round_type, snakes=snakes, candies=candies,
                           max_turns=max_turns)

        # check snake.id refers to an agent
        for snake in self.snakes:
            assert snake.id in self.agents

    def create_snakes(self, grid_size: Tuple[int, int], ids: List[int]) -> List[Snake]:
        snakes = []
        starting_indices = sample(range(grid_size[0] * grid_size[1]), k=len(ids))
        starting_length = 2  # should be > 1 to prevent snakes from going backwards
        for id, index in zip(ids, starting_indices):
            x, y = divmod(index, grid_size[1])
            assert 0 <= x < grid_size[0]
            assert 0 <= y < grid_size[1]
            snakes.append(Snake(id, np.tile([(x, y)], (starting_length, 1))))
        return snakes

    @property
    def grid_size(self):
        return self.state.grid_size

    @property
    def snakes(self):
        return [s for s in self.state.snakes if s is not None]

    @property
    def candies(self):
        return self.state.candies

    @property
    def turn(self):
        return self.state.turn

    @property
    def turns(self):
        return self.state.turns

    @property
    def scores(self):
        return self.state.scores

    @property
    def dead_snakes(self):
        return self.state.dead_snakes

    def update(self):
        snakes = self.state.players_turn()

        moves: List[Tuple[Snake, Move]] = []

        for snake in snakes:
            move_value = self._get_agents_move(snake)
            moves.append((snake, move_value))

        yield from self.state.do_moves(moves)

        self.state.respawn_candies()

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

    def possible_scores(self) -> List[Tuple[int, int]]:
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
                lowest_rank = len([True for s in self.snakes if s is not None])
                score = calculate_final_score(len(snake), lowest_rank)
                possible_scores.append((score, i))
        possible_scores.sort(reverse=True)
        return possible_scores

    def rank(self):
        # TODO: make sure this function can only be called when the game is finished
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
        # TODO: remove this function, instead listen to Finished event
        # if every snake has a score, the game is finished
        return len(self.scores) == len(self.agents)

    def save_replay(self) -> str:
        data = self.state.history.serialize()

        # add the name of the agents
        agents = [None] * len(self.agents)
        for id, agent in self.agents.items():
            index = next(i for i, s in enumerate(self.state.history.initial_snakes) if s.id == id)
            agents[index] = agent.name
        data['agents'] = agents

        # add final ranking if needed
        if self.finished():
            ranking = [None] * len(self.state.history.initial_snakes)
            for id, rank in self.rank().items():
                index = next(i for i, s in enumerate(self.state.history.initial_snakes) if s.id == id)
                ranking[index] = rank
        data['rank'] = ranking

        return data
        # return yaml.safe_dump(data, default_flow_style=True, width=inf)


def move_to_str(move: Move) -> str:
    return 'udlr'[MOVES.index(move)]


def str_to_move(move: str) -> Move:
    assert len(move) == 1
    return MOVES['udlr'.index(move)]


def direction_to_str(direction: np.array) -> str:
    if direction[0] > 0:
        return 'r'
    elif direction[0] < 0:
        return 'l'
    else:
        if direction[1] > 0:
            return 'u'
        elif direction[1] < 0:
            return 'd'
        else:
            return 'p'


def move_str_to_direction(move: str) -> np.array:
    return (UP, DOWN, LEFT, RIGHT, np.array([0, 0]))['udlrp'.index(move)]


def serialize(grid_size, candies, turn, snakes) -> str:
    """
    Serialize a game state to string

    The data is formatted with the following notation. x and y are substituted by the specific coordinate. D indicates
    the direction a segment goes to. A direction can be udlrp (up/down/left/right/in-place)
    1. Grid size: x,y
    2. Candies:   cx,y/x,y/x,y
    3. Turn:      tx
    3. Snakes:    sx,yMMMMMM/x,yMMMMM/x,yMMMMM
    """
    data = f'{grid_size[0]}x{grid_size[1]}c'
    data += '/'.join(f'{candy[0]},{candy[1]}' for candy in candies)
    data += f't{turn}'

    snakedata = []
    for snake in snakes:
        if snake is None:
            continue
        snakestr = f'{snake[0][0]},{snake[0][1]}'
        for i in range(1, len(snake)):
            direction = snake[i] - snake[i - 1]
            snakestr += direction_to_str(direction)
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
    candies = [tuple(int(x) for x in c.split(',')) for c in candies.split('/')] if candies else []
    turn = int(turn)

    snakes = []
    for id, snake in enumerate(snakesstr.split('/')):
        m = re.fullmatch('(\d+),(\d+)(\w+)', snake)
        segment = np.array([int(m.group(1)), int(m.group(2))])
        segments = [segment]
        for s in m.group(3):
            segment = segment + move_str_to_direction(s)
            segments.append(segment)
        snakes.append(Snake(id=id, positions=np.array(segments)))

    return grid_size, candies, turn, snakes
