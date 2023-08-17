import pygame
class Window:
    def __init__(self, display, game, width, height):
        self.game = game
        self.display = display

    def update(self):
        BLACK = (0, 0, 0)
        self.display.fill(BLACK)

