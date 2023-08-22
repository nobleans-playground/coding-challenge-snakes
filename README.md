# Coding Challange: Multiplayer Snake

## Game rule ideas:

We want to promote getting longer and killing other snakes. Which rule should we use to promote this?

- snakes are ranked by how long they have survived. But there is a maximum game length and the snake length is used
- each x turns your snake grows (in addition to eating).

- time limit for calculating the moves? 0.2 max limit per move on average?
- aim for max 5 minutes
- 0.2 second calculation time, 5 steps/second,

Other rules brainstormed:

- when you create a loop, you kill every enemy inside it
- your final score is the highest length achieved
- your final score is the amount of kills achieved
- you are able to accelerate by going straight
- you can discard parts of your body to gain speed
- you have to eat an apple every x game steps, or your snake will die from hunger
- faster movement for longer snakes

## Bot development

To write a bot, you'll have to implement the Bot interface.
After that, make sure it's included in the bots array.

### Executables

#### commandline.py

Battle 2 snakes against each other in the commandline.

#### tournament.py

Battle all bots against eachother in a tournament. It'll write the results to a csv file.

#### gui.py

Battle bots against eachother in a graphical user interface.

#### elo.py

From the tournament results csv you can calculate your bots elo rating.
