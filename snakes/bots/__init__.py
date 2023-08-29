# Copyright 2023 Nobleo Technology B.V.
#
# SPDX-License-Identifier: Apache-2.0

from .example.bot import ExampleBot
from .random import Random
from .hein.bot import ApologeticApophis
from .felipe.bot import TemplateSnake
from .mahmoud.bot import SneakyBot
from .jeroen.bot import ExampleBot as JeroenBot
from .jonothan.bot import helloFellowHumanPerson

bots = (
    Random,
    ExampleBot,
    ApologeticApophis,
    TemplateSnake,
    SneakyBot,
    JeroenBot,
    helloFellowHumanPerson
)
