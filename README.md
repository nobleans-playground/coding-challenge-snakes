<!--
Copyright 2023 Nobleo Technology B.V.

SPDX-License-Identifier: Apache-2.0
-->

# Coding Challange: Multiplayer Snake [![Python application](https://github.com/Rayman/coding-challenge-snakes/actions/workflows/python-app.yml/badge.svg)](https://github.com/Rayman/coding-challenge-snakes/actions/workflows/python-app.yml)

## Current ranking

|Name                       |Wins|Rate  |Matches
|--|--|--|--|
Serpent of the Light        | 84| 93.3% | 90 |
Apologetic Apophis          | 79| 87.8% | 90 |
Explorer                    | 77| 85.6% | 90 |
Bite my shiny metal ass     | 38| 42.2% | 90 |
Slytherin                   | 35| 38.9% | 90 |
Sneaky Snake                | 33| 36.7% | 90 |
Wolverine                   | 33| 36.7% | 90 |
Not a Template              | 32| 35.6% | 90 |
Random                      | 27| 30.0% | 90 |
Greedy Gerard               | 26| 28.9% | 90 |

| Name                | Elo
|--|--|
Serpent of the Light | 2252 |
Apologetic Apophis   | 2161 |
Explorer             | 2072 |
Bite my shiny metal ass | 1278 |
Slytherin            | 1232 |
Sneaky Snake         | 1230 |
Wolverine            | 1221 |
Not a Template       | 1212 |
Random               | 1169 |
Greedy Gerard        | 1172 |

## Description

The goal is to beat all other bots playing snake.
Each match is 1v1, each bot will be paired up with all other opponents.
The bot with the most wins will win the tournament.

You should write your bot's logic in a Python class.
Each turn a function on your bot will be called with the state of the game and the bot needs to decide in which direction to move.

There are two example bots implemented

- [Random](./snakes/bots/random.py)
- [Simple Eater](https://github.com/nobleans-playground/coding-challenge-snakes-bot-template/blob/main/bot.py)

## How the bot interface works

Your bot will be initialized with an id and the size of the grid.
The grid is specified by the amount of tiles in x and y.

```py
def __init__(self, id: int, grid_size: Tuple[int, int]):
```

Each turn your bots `determine_next_move` function will be called.
As in input it'll receive the state of the game.
With this information you should calculate and return which direction it should move in.
After this function call, the move will be applied and then its the turn of the other player.
If you move against a wall or another player, you are dead.

```py
def determine_next_move(self, snakes: List[Snake], candies: List[np.array]) -> Move:
```

How the bot implements this function is up to you.
You can train an AI, do some path planning or implement a method to trap opponents.

## How to submit a bot

Your bot will live as a git submodule inside the main challenge repository.
This means you will need to create your own GitHub account and create a new repository based on a template.
You can follow the following steps to create your own bot.

**Note**: You are allowed to submit a maximum of two bots.

1. Create a GitHub account if you don't have one already.
   Using a personal account is fine.
2. Create a personal repository where your bot will live.
   You can use the following repository template to do this for you: https://github.com/nobleans-playground/coding-challenge-snakes-bot-template
3. Give your bot a custom name and add your name as contributor
   Notify an organizer @Rayman or @heinwessels to add your bot to the challenge as a submodule in the main repository.
   Note: Your bot doesn't have to be complete to be added, it simply needs to run and return a valid move.
   You can update/change/refactor your bot at any point during the challenge.

## Running the bots on your machine

1. Clone this repository using `git clone --recursive git@github.com:Rayman/coding-challenge-snakes.git`.
   The `--recursive` is to pull in all submodule bots.
2. Install all the dependencies
   - **On linux** `sudo apt install -y python3-more-itertools python3-numpy python3-pandas python3-pygame python3-scipy`
   - **On Windows** `pip install -r requirements.txt`
3. Run `tournament.py` or any of the other executables

## Bot development

- If you bot has **NOT** being added to the main repository, create a file in the [./snakes/bots](./snakes/bots) folder.
  Don't forget to add it to the bots list in [./snakes/bots/__init__.py](./snakes/bots/__init__.py).
  See [./snakes/bots/random.py](./snakes/bots/random.py) Random for inspiration
- If you bot has been added to the main repository, just edit the files in your own bots folder.

### Updating your local repository with the newest changes

Over the course of the challenge your local repository might be out-of-date with all the other bots.
To update the environent you can run the following two commands from the root folder.****

```sh
# Pull the latest game-code
git pull
# Pull the latest code from all the bots
git submodule update --remote
```

### Description of all the executables

- **commandline.py**:
  Battle 2 snakes against each other in the commandline.
- **tournament.py**:
  Battle all bots against eachother in a tournament. It'll write the results to a csv file.
- **gui.py**:
  Battle bots against eachother in a graphical user interface. In VSCode, press `F5` to run in debug mode. Use the following command to always have your bot as player 1, battling against a random bot. 

  ```python gui.py --snake1 your-bot-name``` 
- **elo.py**:
  From the tournament results csv you can calculate your bots elo rating.
