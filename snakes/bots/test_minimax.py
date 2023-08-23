import numpy as np

from .minimax import moves_with_scores
from ..constants import Move
from ..snake import Snake


def test_minimax():
    grid_size = (3, 3)
    """
    It's player 0 turn. If you move into corner, you will die
    |0    |
    |0    |
    |  1 1|  
    """
    player = Snake(id=0, positions=np.array([
        [0, 1],
        [0, 2],
    ]))
    opponent = Snake(id=1, positions=np.array([
        [1, 0],
        [2, 0],
    ]))
    candies = [np.array([0, 0])]

    # at depth 0 prefer to move into the corner to eat
    moves = dict(moves_with_scores(grid_size, player, opponent, candies, 0))
    assert moves[Move.UP] == 0
    assert moves[Move.DOWN] == 1
    assert moves[Move.LEFT] == -99
    assert moves[Move.RIGHT] == 0

    # at depth 1 moving to the corner result in the other player growing
    moves = dict(moves_with_scores(grid_size, player, opponent, candies, 1))
    assert moves[Move.UP] == -1
    assert moves[Move.DOWN] == 1
    assert moves[Move.LEFT] == -99
    assert moves[Move.RIGHT] == -1

    # at depth 2 moving to the corner results in death
    moves = dict(moves_with_scores(grid_size, player, opponent, candies, 2))
    assert moves[Move.UP] == -1
    assert moves[Move.DOWN] == -99
    assert moves[Move.LEFT] == -99
    assert moves[Move.RIGHT] == -1
