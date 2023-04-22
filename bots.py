from enum import Enum, auto
from random import choice


class Move(Enum):
    UP = auto()
    DOWN = auto()
    LEFT = auto()
    RIGHT = auto()


class Bot:
    def determine_next_move(self) -> Move:
        pass


class Random(Bot):
    def determine_next_move(self):
        return choice(list(Move))
