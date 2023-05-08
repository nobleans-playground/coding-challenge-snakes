#!/usr/bin/env python3
from argparse import ArgumentParser, FileType

import numpy as np
import pandas
from more_itertools import pairwise
from scipy.optimize import least_squares


def main(infile):
    df = pandas.read_csv(infile)
    print(df)
    print()

    print(f'{"Name":20} First places')
    firsts = df == 1
    for col in df:
        print(f'{col:20} {np.count_nonzero(firsts[col])}')
    print()

    estimate_elo(df)


def estimate_elo(df):
    x0 = np.empty(df.shape[1])
    x0[:] = 1500

    def fun(x):
        residuals = []
        for _, row in df.iterrows():
            for a, b in pairwise(np.argsort(row)):
                rating_a = x[a]
                rating_b = x[b]
                expected = expected_score(rating_a, rating_b)
                # 1 win, 0 loss, 0.5 draw
                actual = (np.sign(row[b] - row[a]) + 1) / 2
                print(f'player {a} vs {b} | {rating_a:.0f} {rating_b:.0f} | {expected:.4} {actual}')
                residuals.append(actual - expected)

        # force elo rating average to be 1500
        residuals.append(np.average(x) - 1500)
        # print(residuals)
        return np.array(residuals)

    res = least_squares(fun, x0)
    for name, elo in zip(df.columns, res.x):
        print(f'{name:20} {elo}')

    expected_scores = expected_score(res.x[:, np.newaxis], res.x[np.newaxis, :])
    print('\nexpected score:\n', np.array_str(expected_scores, precision=2, suppress_small=True))


def expected_score(rating_a, rating_b):
    return 1 / (1 + 10 ** ((rating_b - rating_a) / 400))


if __name__ == '__main__':
    parser = ArgumentParser(description='Elo estimation')
    parser.add_argument('infile', type=FileType(), help="Input csv")
    args = parser.parse_args()

    try:
        main(**vars(args))
    except KeyboardInterrupt:
        pass
