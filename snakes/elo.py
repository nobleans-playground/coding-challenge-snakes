#!/usr/bin/env python3

# Copyright 2023 Nobleo Technology B.V.
#
# SPDX-License-Identifier: Apache-2.0

from math import isnan

import numpy as np
import pandas as pd
from more_itertools import pairwise
from scipy.optimize import least_squares


def estimate_elo(df):
    x0 = np.empty(df.shape[1])
    x0[:] = 1500

    def fun(x):
        # print()
        residuals = []
        for _, row in df.iterrows():
            tmp = np.argsort(row.values)
            for a, b in pairwise(tmp):
                # a & b are the index into the row

                # check if that player participated in that match (otherwise, the rank would be NaN)
                if isnan(row[a]) or isnan(row[b]):
                    continue

                rating_a = x[a]
                rating_b = x[b]
                expected = expected_score(rating_a, rating_b)
                # 1 win, 0 loss, 0.5 draw
                actual = (np.sign(row[b] - row[a]) + 1) / 2

                assert not isnan(actual), (actual, row, a, b)
                # print(f'player {a} vs {b} | {rating_a:.0f} {rating_b:.0f} | {expected:.4} {actual}')
                residuals.append(actual - expected)

        # force elo rating average to be 1500
        residuals.append(np.average(x) - 1500)
        # print(residuals)
        return np.array(residuals)

    res = least_squares(fun, x0)
    return res.x


def expected_score(rating_a, rating_b):
    return 1 / (1 + 10 ** ((rating_b - rating_a) / 400))


def read_csv(filepath_or_buffer):
    return pd.read_csv(filepath_or_buffer, dtype=float)
