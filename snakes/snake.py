# Copyright 2023 Nobleo Technology B.V.
#
# SPDX-License-Identifier: Apache-2.0

from collections.abc import Sequence

import numpy as np


class Snake(Sequence):
    def __init__(self, id, positions):
        assert len(positions.shape) == 2
        assert positions.shape[1] == 2
        self.id = id
        self.positions = positions

    def move(self, move, grow=False):
        if grow:
            self.positions = np.concatenate((self.positions[0:1] + move, self.positions))
        else:
            self.positions[1:] = self.positions[0:-1]
            self.positions[0] += move

    def __iter__(self):
        return iter(self.positions)

    def __len__(self):
        return self.positions.shape[0]

    def __getitem__(self, i):
        return self.positions[i]

    def __repr__(self):
        return f'id={self.id} positions={self.positions.tolist()}'

    def collides(self, pos):
        for p in self.positions:
            if np.array_equal(p, pos):
                return True
        return False
