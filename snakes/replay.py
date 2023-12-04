from typing import Tuple

from .game import RoundType, GameHistory, State


class ReplayReader:
    def __init__(self, doc):
        self.history = GameHistory.deserialize(doc)
        self.state = State(self.history.initial_snakes, self.history.grid_size, RoundType.TURNS,
                           self.history.initial_candies)

    def all_events(self):
        for id_to_move_value in self.history.history:
            if isinstance(id_to_move_value, Tuple):
                self.state.spawn_candy(*id_to_move_value)
            else:
                moves = []
                for s in self.state.snakes:
                    try:
                        move_value = id_to_move_value[s.id]
                        moves.append((s, move_value))
                    except KeyError as e:
                        pass
                for event in self.state.do_moves(moves):
                    yield event
                yield self.state

    def states(self):
        for event in self.all_events():
            if isinstance(event, State):
                yield event
