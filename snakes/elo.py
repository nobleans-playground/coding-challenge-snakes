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

    res = least_squares(fun, x0, verbose=2)
    return res.x


def expected_score(rating_a, rating_b):
    return 1 / (1 + 10 ** ((rating_b - rating_a) / 400))


def print_tournament_summary(df):
    names = [name for name in df.columns if name != 'turns' and not name.startswith('cpu_')]
    ranking = df[names]

    print(f'{"Name":25} Wins   Rate Matches   CPU CPU/t')
    firsts = ranking == 1
    for col in ranking:
        wins = np.count_nonzero(firsts[col])
        matches = np.count_nonzero(np.isfinite(ranking[col]))
        winrate = 100 * wins / matches if matches else float('nan')
        cpu = df['cpu_' + col].sum()
        turns = df['turns'][df[col].notna()].sum()
        cpu_per_turn = cpu / turns
        print(f'{col:25} {np.count_nonzero(firsts[col]):4} {winrate:5.1f}% {matches:7}',
              f'{cpu:5.1f} {cpu_per_turn * 1000:5.1f}')
    print()

    elos = estimate_elo(ranking)

    print(f'{"Name":20} Elo')
    for name, elo in zip(ranking.columns, elos):
        print(f'{name:20} {elo:.0f}')

    expected_scores = expected_score(elos[:, np.newaxis], elos[np.newaxis, :])
    print('\nexpected score:\n', np.array_str(expected_scores, precision=2, suppress_small=True))


def read_csv(filepath_or_buffer):
    return pd.read_csv(filepath_or_buffer, dtype=float)
