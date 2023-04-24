from abc import ABC, abstractmethod
from enum import Enum, auto
from random import choice


class Move(Enum):
    UP = auto()
    DOWN = auto()
    LEFT = auto()
    RIGHT = auto()


class Bot(ABC):
    @property
    @abstractmethod
    def name(self):
        pass

    @abstractmethod
    def determine_next_move(self) -> Move:
        pass


class Random(Bot):
    @property
    def name(self):
        return 'Random'

    def determine_next_move(self):
        return choice(list(Move))
