#!/usr/bin/env python3

# Copyright 2023 Nobleo Technology B.V.
#
# SPDX-License-Identifier: Apache-2.0

from argparse import ArgumentParser, FileType

from snakes.elo import read_csv, print_tournament_summary


def main(infile):
    df = read_csv(infile)
    print_tournament_summary(df)


if __name__ == '__main__':
    parser = ArgumentParser(description='Elo estimation')
    parser.add_argument('infile', type=FileType(), help="Input csv")
    args = parser.parse_args()

    try:
        main(**vars(args))
    except KeyboardInterrupt:
        pass
