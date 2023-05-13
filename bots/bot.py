from abc import abstractmethod, ABC

from constants import Move


class Bot(ABC):
    def __init__(self, id, grid_size):
        self.id = id
        self.grid_size = grid_size

    @property
    @abstractmethod
    def name(self):
        pass

    @abstractmethod
    def determine_next_move(self, snakes, candies) -> Move:
        pass
