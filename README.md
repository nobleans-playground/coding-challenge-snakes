<!--
Copyright 2023 Nobleo Technology B.V.

SPDX-License-Identifier: Apache-2.0
-->

# Coding Challange: Multiplayer Snake [![Python application](https://github.com/nobleans-playground/coding-challenge-snakes/actions/workflows/python-app.yml/badge.svg)](https://github.com/nobleans-playground/coding-challenge-snakes/actions/workflows/python-app.yml)

## Current ranking

|                         | Wins | Rate  | CPU    | CPU/t | Matches | Turns/m | Elo    |
|-------------------------|------|-------|--------|-------|---------|---------|--------|
| Cherries are for Losers | 1171 | 90.1% | 6932.2 | 22.2  | 1300    | 240.6   | 2183.7 |
| Snakunamatata           | 1120 | 86.2% | 94.6   | 0.8   | 1300    | 91.4    | 2089.2 |
| Serpent of the Light    | 1111 | 85.5% | 634.1  | 7.2   | 1300    | 67.8    | 2078.5 |
| FurryMuncher            | 977  | 75.2% | 84.7   | 0.4   | 1300    | 164.1   | 1895.0 |
| Explorer                | 973  | 74.8% | 209.5  | 0.5   | 1300    | 301.4   | 1919.3 |
| Apologetic Apophis      | 926  | 71.2% | 84.2   | 0.2   | 1300    | 285.6   | 1835.5 |
| Sneaky Snake            | 398  | 30.6% | 68.6   | 0.2   | 1300    | 315.8   | 1135.2 |
| Bite my shiny metal ass | 397  | 30.5% | 67.5   | 0.2   | 1300    | 316.7   | 1132.7 |
| Wolverine               | 396  | 30.5% | 58.3   | 0.1   | 1300    | 551.7   | 1128.2 |
| OtterByte               | 394  | 30.3% | 68.5   | 0.2   | 1300    | 318.6   | 1136.1 |
| Random                  | 378  | 29.1% | 126.9  | 0.3   | 1300    | 322.9   | 1119.6 |
| Greedy Gerard           | 378  | 29.1% | 71.0   | 0.2   | 1300    | 326.5   | 1117.4 |
| Not a Template          | 378  | 29.1% | 69.9   | 0.2   | 1300    | 324.5   | 1120.0 |
| Slytherin               | 367  | 28.2% | 67.9   | 0.2   | 1300    | 315.4   | 1109.6 |

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
After this function call, the move will be applied and then it's the turn of the other player.
If you move against a wall or another player, you are dead.

```py
def determine_next_move(self, snakes: List[Snake], candies: List[np.array]) -> Move:
```

How the bot implements this function is up to you.
You can train an AI, do some path planning or implement a method to trap opponents.

## Game rules

1. The exact rules of the game are implemented in [snakes/game.py](./snakes/game.py).
2. If you go out-of-bounds, collide with another bot or return anything other than a Move, your bot will die.
3. The amount of points you get is your longest achieved length.
4. The longest surviving bot will get double the points.
   This promotes eating candies, otherwise bots will stay short and hide in the corner.
5. There is a maximum turn limit of 10k turns (see [snakes/constants.py](./snakes/constants.py)).
   If there is no winner after these amount of turns have passed, the game is ended, both players survived the longest.

## Tournament rules

1. You are allowed to submit a maximum of two bots.
2. Your bot must be your own creation.
This rule is so that you may not blatantly copy someone's bot, change only a few lines, and then submit it as your own.
*Some* code duplication is of course inevitable and thus allowed, because the logic might be similar between bots.
3. The code of the game is law.
The rules of the game are implemented in the code.
If you want to know the specific rules of the game, please look at the code.
If the game determines you've won a game, that is the outcome.
4. Please limit the processing time of your bot.
Currently, there's a hard limit of `100ms` _average_ time-per-move as measured by [tournament.py](./tournament.py).
Please talk to one of the organizers if you think this is too short.
You can also use a profiler to try and make your code faster.
5. You can only use the Python libraries that are in the [requirements.txt](./requirements.txt) file.
If you want to use another library, please let one of the organizers know.
6. Multithreading is not allowed
7. Targeting a specific other bot is not allowed, although you may target the tactics of a general class of bot.
This means you are not allowed to use a bots ID to apply a specific strategy.
This also means is also not allowed to detect your other bot and 'suicide' when encountered.
8. You are not allowed to read or alter the game's internal state, or the state of the other bot.
You can only use the information that is given via the interface.

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

1. Clone this repository using `git clone --recursive git@github.com:nobleans-playground/coding-challenge-snakes.git`.
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
