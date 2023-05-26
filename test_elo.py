from io import StringIO
from statistics import mean

from pytest import approx

from elo import estimate_elo, read_csv


def test_1v1():
    """
    A winrate of 75% would be an elo difference of 190.85 elo points
    """
    csv = """Bot1,Bot2
1,2
1,2
1,2
2,1
    """
    df = read_csv(StringIO(csv))
    elos = estimate_elo(df)
    assert elos[0] - elos[1] == approx(190.85, 1e-5)
    assert mean(elos) == approx(1500)


def test_3_player():
    """
    A winrate of 75% would be an elo difference of 190.85 elo points

    So suppose we have 3 players (A, B, C) with elo (1000, 1190.85, 1381.70)

    Expected winrates:
    AB = 75%
    BC = 75%
    AC = 99.9%
    """

    csv = """Bot1,Bot2,Bot3
1,2
1,2
1,2
2,1
,1,2
,1,2
,1,2
,2,1
    """
    df = read_csv(StringIO(csv))
    elos = estimate_elo(df)
    assert elos[0] - elos[1] == approx(190.85, 1e-5)
    assert elos[1] - elos[2] == approx(190.85, 1e-5)
    assert mean(elos) == approx(1500)


def test_multiple_players():
    csv = """Bot1,Bot2,Bot3,Bot4,Bot5,Bot6,Bot7
1,2
,1,2
,,1,2
,,,1,2
,,,,1,2
,,,,,1,2
"""
    df = read_csv(StringIO(csv))
    estimate_elo(df)


def test_deathmatch():
    csv = """Bot1,Bot2,Bot3,Bot4,Bot5,Bot6,Bot7
5,3,4,1,2
    """
    df = read_csv(StringIO(csv))
    estimate_elo(df)
