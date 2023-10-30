# Copyright 2023 Nobleo Technology B.V.
#
# SPDX-License-Identifier: Apache-2.0

from .example.bot import ExampleBot
from .random import Random
from .hein.bot import ApologeticApophis
from .felipe.bot import TemplateSnake
from .mahmoud.bot import SneakyBot
from .jeroen.bot import ExampleBot as JeroenBot
from .jonothan.bot import bender
from .lewie.bot import LewieBot
from .bram.bot import Slytherin
from .daniel.bot import Explorer
from .rokusottervanger.bot import OtterByte
from .mukunda.bot import Snakunamatata
from .ferry.bot import FurryMuncher
from .mhoogesteger.bot import CherriesAreForLosers
from .mhoogesteger.bot_pathfinding_wip import ThereIsNoCandy
# from .brammmieee.bot import RLQuaza

bots = (
    # Random,
    # ExampleBot,  # Disabled: Template
    ApologeticApophis,
    # TemplateSnake,  # Disabled: Template not modified
    # SneakyBot,  # Disabled: Template not modified
    JeroenBot,
    bender,
    LewieBot,
    # Slytherin,  # Disabled: Template not modified
    Explorer,
    # OtterByte,  # Disabled: Template not modified
    Snakunamatata,
    FurryMuncher,
    CherriesAreForLosers,
    ThereIsNoCandy,
    # RLQuaza,  # Disabled: makes tournament.py freeze
)
