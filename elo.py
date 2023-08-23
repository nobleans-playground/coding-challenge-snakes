#!/usr/bin/env python3
from argparse import ArgumentParser, FileType

import numpy as np

from snakes.elo import estimate_elo, expected_score, read_csv


def main(infile):
    df = read_csv(infile)
    print(df)
    print()

    print(f'{"Name":20} First places')
    firsts = df == 1
    for col in df:
        print(f'{col:20} {np.count_nonzero(firsts[col])}')
    print()

    elos = estimate_elo(df)

    print(f'{"Name":20} Elo')
    for name, elo in zip(df.columns, elos):
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
