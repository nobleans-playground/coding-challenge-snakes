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
    return pd.Series(res.x, index=df.columns)


def expected_score(rating_a, rating_b):
    return 1 / (1 + 10 ** ((rating_b - rating_a) / 400))


def print_tournament_summary(df):
    names = [name for name in df.columns if name != 'turns' and not name.startswith('cpu_')]
    cpu_names = ['cpu_' + name for name in names]

    ranking = df[names]  # contains only the individual match rankings

    data = {
        'Wins': (ranking == 1).sum(),
        'Matches': ranking.notna().sum(),
        'CPU': df[cpu_names].sum().rename(dict(zip(cpu_names, names))),
        'Turns': calculate_turns(df, names)
    }

    data = pd.DataFrame(data)

    data['Rate'] = data['Wins'] / data['Matches']
    data['CPU/t'] = 1000 * data['CPU'] / data['Turns']
    data['Turns/m'] = data['Turns'] / data['Matches']

    # reorder columns
    data = data[['Wins', 'Rate', 'CPU', 'CPU/t', 'Matches']]
    data.sort_values('Wins', inplace=True, ascending=False)

    # rounding before display
    data['Rate'] = data['Rate']
    data['CPU'] = data['CPU']
    data['CPU/t'] = data['CPU/t']

    print(data.to_string(formatters={'Rate': '{:,.1%}'.format, 'CPU': '{:.1f}'.format, 'CPU/t': '{:.1f}'.format,
                                     'Elo': '{:.1f}'.format}))

    data['Elo'] = estimate_elo(ranking)

    print()
    print(data.to_string(formatters={'Rate': '{:,.1%}'.format, 'CPU': '{:.1f}'.format, 'CPU/t': '{:.1f}'.format,
                                     'Elo': '{:.1f}'.format}))


def calculate_turns(df, names):
    turns = {}
    for col in df[names]:
        turns[col] = df['turns'][df[col].notna()].sum()
    return pd.Series(turns)


def read_csv(filepath_or_buffer):
    df = pd.read_csv(filepath_or_buffer, dtype=float)
    if 'turns' in df.columns:
        df = df.astype({'turns': int})
    return df
