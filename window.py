# WHITE = (200, 200, 200)
# WINDOW_HEIGHT = 400
# WINDOW_WIDTH = 400
import pygame


class Window:
    def __init__(self, width, height):
        self.screen = pygame.display.set_mode((width, height))

    def update(self):
        BLACK = (0, 0, 0)
        self.screen.fill(BLACK)

# def drawGrid():
#     blockSize = 20  # Set the size of the grid block
#     for x in range(0, WINDOW_WIDTH, blockSize):
#         for y in range(0, WINDOW_HEIGHT, blockSize):
#             rect = pygame.Rect(x, y, blockSize, blockSize)
#             pygame.draw.rect(SCREEN, WHITE, rect, 1)
