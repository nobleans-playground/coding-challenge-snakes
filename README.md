# Coding Challange: Multiplayer Snake [![Python application](https://github.com/Rayman/coding-challenge-snakes/actions/workflows/python-app.yml/badge.svg)](https://github.com/Rayman/coding-challenge-snakes/actions/workflows/python-app.yml)

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
def __init__(self, id: int, grid_size: tuple[int, int]):
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
I've asked ChatGPT which algorithms could be suitable for a multiplayer snake game.

- **Greedy Algorithm**: Bot always moves towards the nearest food.
- **Avoid Collisions**: Bot focuses on avoiding collisions with itself, walls, and opponents.
- **Chase and Evade**: Bot alternates between getting closer to opponents and maintaining a safe distance.
- **Wall Following**: Bot follows the game arena's walls to stay safe and create trapping opportunities.
- **Random Moves with Avoidance**: Bot makes random moves while avoiding collisions.
- **Food Proximity**: Bot moves towards the nearest food while avoiding getting too close to opponents.
- **Longest Path**: Bot chooses moves leading to the longest possible path before collisions.
- **Stay Central**: Bot aims to stay near the center of the game arena for better maneuverability.

It also came up with some more advanced algorithms.

- **Minimax with Alpha-Beta Pruning**: Decision-making by exploring moves and opponent responses, optimizing with alpha-beta - pruning.
- **Monte Carlo Tree Search (MCTS)**: Balancing random simulations and tree traversal to find optimal moves.
- **Reinforcement Learning (RL)**: Learning best strategies through trial and error, maximizing rewards over interactions.
- **Heuristic-Based Approaches**: Using predefined rules based on game factors to guide decision-making.
- **Neural Networks**: Training networks to map game states to optimal moves using supervised or reinforcement learning.
- **Evolutionary Algorithms**: Evolving bot strategies over generations based on performance and mutation.

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
  Battle bots against eachother in a graphical user interface.
- **elo.py**:
  From the tournament results csv you can calculate your bots elo rating.
