#!/usr/bin/env python3

# Copyright 2023 Nobleo Technology B.V.
#
# SPDX-License-Identifier: Apache-2.0

from argparse import ArgumentParser, FileType
from typing import Tuple

import yaml

from snakes.game import RoundType, print_event, GameHistory, State
from snakes.utils import Printer


def main(match, compare, seed):
    for doc in yaml.safe_load_all(match):
        print('Start replay')
        history = GameHistory.deserialize(doc)
        state = State(history.initial_snakes, history.grid_size, RoundType.TURNS, history.initial_candies)
        print(state)
        print(history)

        printer = Printer()
        printer.print(state)
        print('here!!!')
        for id_to_move_value in history.history:
            if isinstance(id_to_move_value, Tuple):
                state.spawn_candy(*id_to_move_value)
            else:
                moves = []
                for s in state.snakes:
                    try:
                        move_value = id_to_move_value[s.id]
                        moves.append((s, move_value))
                    except KeyError as e:
                        pass
                for event in state.do_moves(moves):
                    print_event(event, 'TODO')
                printer.print(state)


if __name__ == '__main__':
    parser = ArgumentParser(description='Replay a match')
    parser.add_argument('match', type=FileType('r'), help="Input match database")
    parser.add_argument('--compare', help="Compare moves with another bot")
    parser.add_argument('-s', '--seed', type=int, help='Random seed')
    args = parser.parse_args()

    try:
        main(**vars(args))
    except KeyboardInterrupt:
        pass
