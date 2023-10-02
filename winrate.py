#!/usr/bin/env python3

# Copyright 2023 Nobleo Technology B.V.
#
# SPDX-License-Identifier: Apache-2.0

from argparse import ArgumentParser, FileType

import numpy as np
import pandas as pd
from matplotlib import pyplot as plt

from snakes.elo import read_csv


def print_winrate(df):
    reserved_names = ['turns', 'seed']
    names = [name for name in df.columns if name not in reserved_names and not name.startswith('cpu_')]
    cpu_names = ['cpu_' + name for name in names]

    ranking = df[names]  # contains only the individual match rankings

    data = {
        'Wins': (ranking == 1).sum(),
    }

    data = pd.DataFrame(data)
    data.sort_values('Wins', inplace=True, ascending=False)

    winrate = pd.DataFrame(np.full((len(names), len(names)), np.nan), index=data.index, columns=data.index)
    for a in data.index:
        for b in data.index:
            if a == b:
                continue
            matches_participated = ranking[ranking[a].notna() & ranking[b].notna()]
            won = (matches_participated[a] < matches_participated[b]).sum()
            winrate[a][b] = won / len(matches_participated)

    print(winrate.T)

    fig = plt.figure()
    ax = fig.add_subplot(111)
    cax = ax.matshow(winrate.T, interpolation='nearest')
    fig.colorbar(cax)
    ax.set_xticks(range(len(data.index)))
    ax.set_xticklabels(data.index, rotation=90)
    ax.set_yticks(range(len(data.index)))
    ax.set_yticklabels(data.index)
    plt.show()


def main(infile):
    df = read_csv(infile)
    print_winrate(df)


if __name__ == '__main__':
    parser = ArgumentParser(description='Elo estimation')
    parser.add_argument('infile', type=FileType(), help="Input csv")
    args = parser.parse_args()

    try:
        main(**vars(args))
    except KeyboardInterrupt:
        pass
