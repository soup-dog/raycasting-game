# pygame
import pygame
from pygame.event import Event
from pygame.time import Clock
from pygame.surface import Surface
from pygame import Color
# numpy
import numpy as np
# standard
from enum import Enum
# project
from game_map import MapHelper
# typing
from typing import Callable
from numpy.typing import NDArray

pygame.init()


class RaycastingGame:
    class DrawMode(Enum):
        GAME = 0
        MAP = 1

    DrawMethod = Callable[[Surface], None]

    def __init__(self, background_colour: Color = (255, 255, 255)):
        self.background_colour = background_colour

        self.clock: Clock = Clock()
        self.running: bool = False
        self.key_map: dict[int, Callable[[], None]] = {
            pygame.K_ESCAPE: self.quit
        }
        self.draw_mode_map: dict[RaycastingGame.DrawMode, RaycastingGame.DrawMethod] = {
            RaycastingGame.DrawMode.GAME: self.draw_game,
            RaycastingGame.DrawMode.MAP: self.draw_map
        }
        self.map: NDArray[np.uint8] = MapHelper.generate_random_map((16, 16))
        self.draw_mode: RaycastingGame.DrawMode = RaycastingGame.DrawMode.MAP

    def quit(self):
        self.running = False

    def process_events(self, events: list[Event]):
        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key in self.key_map.keys():
                    self.key_map[event.key]()

    def update(self):
        delta_time = self.clock.tick()
        self.process_events(pygame.event.get())

    def draw(self, surface: Surface):
        surface.fill(self.background_colour)
        self.draw_mode_map[self.draw_mode](surface)

    def draw_map(self, surface: Surface):
        cell_height = int(surface.get_height() / self.map.shape[0])
        cell_width = cell_height

        centre_offset_x = (surface.get_width() - cell_width * self.map.shape[0]) / 2
        centre_offset_y = (surface.get_height() - cell_height * self.map.shape[1]) / 2

        for row in range(self.map.shape[0]):
            for col in range(self.map.shape[1]):
                if self.map[row, col]:
                    colour = (255, 0, 0)
                else:
                    colour = (0, 0, 0)
                rect = (
                    col * cell_width + centre_offset_x,
                    row * cell_height + centre_offset_y,
                    cell_width,
                    cell_height
                )
                pygame.draw.rect(surface, colour, rect)

    def draw_game(self, surface: Surface):
        pass

    def mainloop(self):
        window = pygame.display.set_mode((0, 0))

        self.running = True

        while self.running:
            self.update()
            self.draw(window)
            pygame.display.flip()


if __name__ == '__main__':
    game = RaycastingGame()

    game.mainloop()
