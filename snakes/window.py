# Copyright 2023 Nobleo Technology B.V.
#
# SPDX-License-Identifier: Apache-2.0

import math
from abc import abstractmethod
from enum import Enum, auto
import numpy as np
from random import choice

import pygame
from snakes.bots import bots
from snakes.game import Game
from commandline import levenshtein_ratio

BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)

COLOURS = [
    (230, 25, 75),
    (60, 180, 75),
    (255, 225, 25),
    (0, 130, 200),
    (245, 130, 48),
    (145, 30, 180),
    (70, 240, 240),
    (240, 50, 230),
    (210, 245, 60),
    (250, 190, 212),
    (0, 128, 128),
    (220, 190, 255),
    (170, 110, 40),
    (255, 250, 200),
    (128, 0, 0),
    (170, 255, 195),
    (128, 128, 0),
    (255, 215, 180),
    (0, 0, 128),
    (128, 128, 128),
]

TEAM_A = (230, 25, 75)
TEAM_B = (60, 180, 75)
BUTTON = (51, 51, 51)
POPUP = (36, 36, 36)


class GameState(Enum):
    RUNNING = auto()
    FINISHED = auto()
    IDLE = auto()
    STEP = auto()


class Window:
    def __init__(self, window, width, height, snake1=None, snake2=None):
        self.game_state = GameState.RUNNING
        self.window = window
        self.width = width
        self.height = height

        # These `i`'s do not represent the player number
        self.all_bots = {i: Agent for i, Agent in enumerate(bots)}

        # Determine which bots will play the game
        agents = {}
        names = [Bot(id=i, grid_size=(1, 1)).name for i, Bot in enumerate(bots)]
        if snake1:
            name_matches = [levenshtein_ratio(name, snake1) for name in names]
            agents[0] = self.all_bots[np.argmax(name_matches)]
        else:
            agents[0] = choice(self.all_bots)
        if snake2: 
            name_matches = [levenshtein_ratio(name, snake2) for name in names]
            agents[1] = self.all_bots[np.argmax(name_matches)]
        else:
            agents[1] = choice(self.all_bots)
        
        # Create the first game with the first two bots
        # The ID's will always represent the player number
        self.game = Game(agents=agents)

        # Some GUI stuff
        pygame.font.init()
        self.buttons = []
        self.popup = None
        self.border = 8

        # The scoreboard is where all the scores will be printed
        self.scoreboard = pygame.Surface(self.window.get_size())
        self.font = pygame.font.SysFont(None, 24)

        # Create some constants (assuming area is square)
        self.tile_size = math.floor(min(self.window.get_size()) / self.game.grid_size[1])
        self.body_size = math.floor(self.tile_size * 0.9)
        self.body_tile_offset = (self.tile_size - self.body_size) / 2
        self.candy_radius = int(self.tile_size * 0.6 / 2)

    class Popup:
        def __init__(self, **kwargs):
            self.parent = kwargs.get("parent")
            self.root = kwargs.get("root", self.parent)

            self.width = kwargs.get("width")
            self.height = kwargs.get("height")
            self.background_colour = kwargs.get("background_colour", POPUP)

            self.buttons = []

        def draw(self):
            left = self.parent.width / 2 - self.width / 2
            right = left + self.width
            top = self.parent.height / 2 - self.height / 2
            bottom = top + self.height

            pygame.draw.rect(
                self.parent.window,
                self.background_colour,
                (left, top, self.width, self.height))

            self.draw_concrete()

        @abstractmethod
        def draw_concrete(self):
            pass

        @abstractmethod
        def on_exit(self):
            pass

    class PlayerSelectionPopup(Popup):
        def __init__(self, **kwargs):
            super().__init__(**kwargs)
            self.player = kwargs.get("player")

        def on_exit(self, bot_id):
            # Start new game
            self.root.restart_game({'agent_id': self.player, 'bot_id': bot_id})

            # Close the popup
            self.root.popup = None
            self.root.game_state = GameState.RUNNING

        def draw_concrete(self):
            border = self.parent.border
            left = self.parent.width // 2 - self.width // 2
            right = left + self.width
            top = self.parent.height // 2 - self.height // 2
            bottom = top + self.height

            button_left = left + border
            button_top = top + border
            button_width = (self.width - 4 * border) // 2
            button_height = 30
            for bot_id, bot in self.root.all_bots.items():
                self.root.button(
                    text=bot(0,(1,1)).name, # Need an object to get the name
                    position=[button_left, button_top],
                    width=button_width,
                    height=button_height,
                    align="left",
                    parent=self,
                    window=self.parent.window,
                    
                    # Need to capture the value explicitly
                    callback=lambda bot_id=bot_id : self.on_exit(bot_id),                    
                )

                button_top += button_height + border

    class Button:
        def __init__(self, **kwargs):
            self.parent = kwargs.get("parent")
            self.root = kwargs.get("root", self.parent)
            self.position = kwargs.get("position")
            self.width = kwargs.get("width")
            self.height = kwargs.get("height")
            self.text = kwargs.get("text", None)
            self.callback = kwargs.get("callback")
            self.background_colour = kwargs.get("background_colour", BUTTON)
            self.foreground_colour = kwargs.get("foreground_colour", WHITE)

            self.hover_outline = WHITE
            self.align = kwargs.get("align", "center")

            self.window = self.root.window
            self.font = pygame.font.SysFont(None, self.height)

            pygame.draw.rect(self.window, self.background_colour, (*self.position, self.width, self.height))

            if self.text:
                text_object = self.font.render(self.text, True, WHITE)
                text_size = self.font.size(self.text)

                if self.align == "center":
                    self.window.blit(text_object, (
                        self.position[0] + self.width / 2 - text_size[0] / 2,
                        self.position[1] + self.height / 2 - text_size[1] / 2
                    ))
                elif self.align == "left":
                    self.window.blit(text_object, (
                        self.position[0] + self.root.border,
                        self.position[1] + self.height / 2 - text_size[1] / 2
                    ))
                else:
                    RuntimeError("Oops")

        def do_hover(self):
            pygame.draw.rect(self.window, self.hover_outline, (*self.position, self.width, self.height), 3)

        def is_at_position(self, position):
            return position[0] >= self.position[0] and position[0] <= self.position[0] + self.width and \
                position[1] >= self.position[1] and position[1] <= self.position[1] + self.height

    def set_state(self, state):
        self.game_state = state

    def restart_game(self, new_agent=None):
        # extract types from agent objects
        agents = {i: type(agent) for i, agent in self.game.agents.items()}
        
        if new_agent:
            # Replace one of the snakes
            agents[new_agent['agent_id']] = self.all_bots[new_agent['bot_id']]

        # Setup new game with this snake
        self.game = Game(agents)

    def handle_click(self, position):
        # Prioritize popup buttons
        for button in self.popup.buttons if self.popup else self.buttons:
            if button.is_at_position(position):
                button.callback()
                return # Only handle one button at a time

    def handle_mouse_hovers(self, buttons):
        mouse = pygame.mouse.get_pos()
        for button in buttons:
            if button.is_at_position(mouse):
                button.do_hover()

    def button(self, **kwargs):
        root = kwargs.get("root", self)
        kwargs["root"] = root  # Ensure it's set
        parent = kwargs.get("parent", self)
        kwargs["parent"] = parent  # Ensure it's set
        parent.buttons += [self.Button(**kwargs)]

    def update(self):
        if self.game_state == GameState.RUNNING or self.game_state == GameState.STEP:
            if not self.game.finished():
                self.game.update()
            if self.game_state == GameState.STEP:
                self.game_state = GameState.IDLE
        if self.game.finished():
            self.game_state = GameState.FINISHED

        self.window.fill(BLACK)
        self.buttons = []  # This is so inefficient.

        self.update_information()
        self.draw_arena()

        if self.popup:
            self.popup.buttons = []  # This is so inefficient.
            self.popup.draw()
            self.handle_mouse_hovers(self.popup.buttons)
        else:
            self.handle_mouse_hovers(self.buttons)

    def draw_arena(self):
        # Draw snake
        for snake in self.game.snakes:
            for position in snake:
                pygame.draw.rect(self.window, COLOURS[snake.id], (
                    (position[0] * self.tile_size) + self.body_tile_offset,
                    self.height - ((position[1] * self.tile_size)) - self.tile_size + self.body_tile_offset,
                    self.body_size, self.body_size
                ))

        # Draw candies
        for candy in self.game.candies:
            pygame.draw.circle(self.window, COLOURS[-1], (
                int((candy[0] + 0.5) * self.tile_size),
                self.height - (int((candy[1] + 0.5) * self.tile_size)),
            ), self.candy_radius)

    def start_bot_selection_popup(self, player):
        self.game_state = GameState.IDLE
        self.popup = self.PlayerSelectionPopup(
            parent=self,
            root=self,
            width=math.floor(self.width * 0.7),
            height=math.floor(self.height * 0.7),
            player=player,
        )

    def update_information(self):
        # Draw the information part
        left = self.height + self.border
        right = self.width - self.border
        top = self.border
        bottom = self.height - self.border

        player_emblem_height = 60

        for score, index in self.game.possible_scores():
            # for index, colour in enumerate([TEAM_A, TEAM_B]):
            # if index >= len(self.game.snakes): continue
            self.button(
                position=[left, top],
                width=right - left,
                height=player_emblem_height,
                background_colour=[TEAM_A, TEAM_B][index % 2],
                callback=lambda index=index: self.start_bot_selection_popup(index)
            )

            # Draw Name
            text_to_render = self.game.agents[index].name
            font = pygame.font.SysFont(None, 32)
            text_size = font.size(text_to_render)
            text_object = font.render(text_to_render, True, WHITE)
            self.window.blit(text_object, (left + self.border, top + self.border))

            # Draw contributor
            text_to_render = self.game.agents[index].contributor
            font = pygame.font.SysFont(None, 26)
            text_object = font.render(text_to_render, True, WHITE)
            self.window.blit(text_object, (left + self.border, top + self.border + text_size[1] + self.border))

            # Draw score
            font = pygame.font.SysFont(None, 68)
            text_to_render = f"{score}"
            text_size = font.size(text_to_render)
            text_object = font.render(text_to_render, True, WHITE)
            self.window.blit(text_object, (right - self.border - text_size[0], top + self.border))

            top += player_emblem_height + self.border

        button_amount = 4
        button_height = 30
        button_width = (self.width - self.height - (button_amount + 1) * self.border) // button_amount
        button_top = bottom - button_height
        button_left = left

        # Button panel
        self.button(
            text="Run",
            position=[button_left, button_top],
            width=button_width,
            height=button_height,
            callback=lambda: self.set_state(GameState.RUNNING)
        )

        button_left += button_width + self.border
        self.button(
            text="Step",
            position=[button_left, button_top],
            width=button_width,
            height=button_height,
            callback=lambda: self.set_state(GameState.STEP)
        )

        button_left += button_width + self.border
        self.button(
            text="Stop",
            position=[button_left, button_top],
            width=button_width,
            height=button_height,
            callback=lambda: self.set_state(GameState.IDLE)
        )

        button_left += button_width + self.border
        self.button(
            text="Restart",
            position=[button_left, button_top],
            width=button_width,
            height=button_height,
            callback=lambda: self.restart_game()
        )
