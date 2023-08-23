from .bot import Bot
from .example.bot import SimpleEater
from .minimax import MiniMax
from .simple_bots import Random, SimpleAvoidEater

_ = Bot

bots = (Random, SimpleEater, SimpleAvoidEater, MiniMax)
