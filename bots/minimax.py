from copy import deepcopy
from random import choice
from typing import List

import numpy as np
from constants import MOVE_VALUE_TO_DIRECTION, Move
from game import Snake

from .bot import Bot


def moves_with_scores(grid_size, player, opponent, candies, depth):
    for move_value, move in MOVE_VALUE_TO_DIRECTION.items():
        p = deepcopy(player)
        for i, candy in enumerate(candies):
            if np.array_equal(p[0] + move, candy):
                p.move(move, grow=True)
                break
        else:
            p.move(move)
        node = Node(grid_size, p, opponent, candies)
        value = -negamax(node, depth, 1)
        yield move_value, value


def negamax(node, depth, color):
    # print(f'depth={depth} color={color}')
    value: float
    if depth == 0 or node.is_terminal_node():
        value = -node.heuristic_value()
    else:
        values = []
        for child in node.children():
            values.append(-negamax(child, depth - 1, -color))
        # print(f'values={values}')
        value = max(values)
    # print(f'depth={depth} value={value:3} color={color} node=\n{node}')
    return value


class Node:
    def __init__(self, grid_size, player: Snake, opponent: Snake, candies: List[np.array]):
        self.grid_size = grid_size
        self.player = player
        self.opponent = opponent
        self.candies = candies

    def is_terminal_node(self):
        if not is_on_grid(self.player[0], self.grid_size):
            # print('player moved out of the game')
            return True
        for p in self.player[1:]:
            if np.array_equal(p, self.player[0]):
                # print('self collision')
                return True
        if collides(self.player[0], self.opponent):
            # print('player collided')
            return True
        return False

    def heuristic_value(self):
        if self.is_terminal_node():
            return -99
        return len(self.player) - len(self.opponent)

    def children(self):
        for move in MOVE_VALUE_TO_DIRECTION.values():
            player = deepcopy(self.opponent)
            for i, candy in enumerate(self.candies):
                if np.array_equal(player[0] + move, candy):
                    player.move(move, grow=True)
                    break
            else:
                player.move(move)
            yield Node(self.grid_size, player, self.player, self.candies)

    def __str__(self):
        grid = np.empty(self.grid_size, dtype=str)
        for x in range(self.grid_size[0]):
            for y in range(self.grid_size[1]):
                grid[x, y] = ' '
        for candy in self.candies:
            grid[candy[0], candy[1]] = '*'
        if not self.is_terminal_node():
            # if the player died, don't print it
            for pos in self.player:
                grid[pos[0], pos[1]] = 'P'
        for pos in self.opponent:
            grid[pos[0], pos[1]] = 'O'
        return str(np.flipud(grid.T))


def is_on_grid(pos, grid_size):
    return 0 <= pos[0] < grid_size[0] and 0 <= pos[1] < grid_size[1]


def collides(head, snake):
    for segment in snake:
        if np.array_equal(head, segment):
            return True
    return False


class MiniMax(Bot):
    """
    Pick a random move, given that it is collision free
    """

    @property
    def name(self):
        return 'Minimax'

    def determine_next_move(self, snakes, candies) -> Move:
        player = [snake for snake in snakes if snake.id == self.id]
        opponent = [snake for snake in snakes if snake.id != self.id]
        assert len(player) == 1
        assert len(opponent) == 1
        player = player[0]
        opponent = opponent[0]

        max_score = float('-inf')
        moves = []
        for move, score in moves_with_scores(self.grid_size, player, opponent, candies, 2):
            if score > max_score:
                max_score = score
                moves = [move]
            if score == max_score:
                moves.append(move)
        return choice(moves)
