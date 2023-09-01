#!/usr/bin/env python3

# Copyright 2023 Nobleo Technology B.V.
#
# SPDX-License-Identifier: Apache-2.0

from argparse import ArgumentParser, FileType

import numpy as np

from snakes.elo import estimate_elo, expected_score, read_csv


def main(infile):
    df = read_csv(infile)
    names = [name for name in df.columns if name != 'turns']
    ranking = df[names]

    print(f'{"Name":25} Wins  Rate  Matches')
    firsts = ranking == 1
    for col in ranking:
        wins = np.count_nonzero(firsts[col])
        matches = np.count_nonzero(np.isfinite(ranking[col]))
        print(f'{col:25} {np.count_nonzero(firsts[col]):4} {100 * wins / matches:5.1f}% {matches}')
    print()

    elos = estimate_elo(ranking)

    print(f'{"Name":20} Elo')
    for name, elo in zip(ranking.columns, elos):
        print(f'{name:20} {elo:.0f}')

    expected_scores = expected_score(elos[:, np.newaxis], elos[np.newaxis, :])
    print('\nexpected score:\n', np.array_str(expected_scores, precision=2, suppress_small=True))


if __name__ == '__main__':
    parser = ArgumentParser(description='Elo estimation')
    parser.add_argument('infile', type=FileType(), help="Input csv")
    args = parser.parse_args()

    try:
        main(**vars(args))
    except KeyboardInterrupt:
        pass
