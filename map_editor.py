import argparse
from typing import Callable
import pygame
from pygame import Surface
from pygame.freetype import SysFont
import numpy as np
from game_map import Map, MapHelper

pygame.init()


class Editor:
    def __init__(self, width: int, height: int, path: str):
        self.path = path
        self.map: Map = np.zeros((width, height), dtype=np.uint8)
        self.selected_cell = np.zeros((2, ), dtype=int)
        self.running: bool = False
        self.stroke: int = 0
        self.key_map: dict[int, Callable] = {
            pygame.K_ESCAPE: self.quit,
            pygame.K_LEFT: self.left,
            pygame.K_RIGHT: self.right,
            pygame.K_UP: self.up,
            pygame.K_DOWN: self.down,
            pygame.K_EQUALS: self.add_stroke,
            pygame.K_MINUS: self.sub_stroke,
            pygame.K_RETURN: self.draw_stroke,
            pygame.K_f: self.fill,
        }
        self.cell_size: float = 0

    def left(self):
        self.selected_cell[1] -= 1
        self.validate_selected_cell()

    def right(self):
        self.selected_cell[1] += 1
        self.validate_selected_cell()

    def up(self):
        self.selected_cell[0] -= 1
        self.validate_selected_cell()

    def down(self):
        self.selected_cell[0] += 1
        self.validate_selected_cell()

    def add_stroke(self):
        self.stroke += 1
        if self.stroke > 255:
            self.stroke = 0

    def sub_stroke(self):
        self.stroke -= 1
        if self.stroke < 0:
            self.stroke = 255

    def draw_stroke(self):
        self.map[self.selected_cell[0], self.selected_cell[1]] = self.stroke

    def fill(self):
        self.map[:] = self.stroke

    def validate_selected_cell(self):
        self.selected_cell[0] %= self.map.shape[0]
        self.selected_cell[1] %= self.map.shape[1]

    def quit(self):
        self.running = False
        MapHelper.save_map_file(self.path, self.map)

    def draw_map(self, surface: Surface):
        cell_size = int(self.cell_size)

        font = SysFont("", cell_size)

        highest_value = np.max(self.map)

        for row in range(self.map.shape[0]):
            for col in range(self.map.shape[1]):
                cell_value = self.map[row, col]
                brightness = 255 * (0 if highest_value == 0 else cell_value / highest_value)

                if self.selected_cell[0] == row and self.selected_cell[1] == col:
                    brightness = 255

                inverted_brightness = 255 - brightness

                screen_x = col * cell_size
                screen_y = row * cell_size

                pygame.draw.rect(surface,
                                 (brightness, brightness, brightness),
                                 (screen_x, screen_y, cell_size, cell_size))
                font.render_to(surface,
                               (screen_x, screen_y),
                               str(cell_value),
                               fgcolor=(inverted_brightness, inverted_brightness, inverted_brightness))

        map_width = cell_size * self.map.shape[1]

        font.render_to(surface, (map_width, 0), str(self.stroke))

    def draw(self, surface: Surface):
        surface.fill((255, 255, 255))
        self.draw_map(surface)
        pygame.display.flip()

    def process_events(self, events: list[pygame.event.Event]):
        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key in self.key_map.keys():
                    self.key_map[event.key]()

        if pygame.mouse.get_pressed(3)[0]:
            mouse_pos = pygame.mouse.get_pos()
            cell_x = int(mouse_pos[0] / self.cell_size)
            cell_y = int(mouse_pos[1] / self.cell_size)

            self.selected_cell = np.array([cell_y, cell_x], dtype=int)
            self.validate_selected_cell()
            self.draw_stroke()

    def mainloop(self):
        window = pygame.display.set_mode((0, 0))

        self.cell_size = int(window.get_height() / self.map.shape[0])

        self.running = True

        while self.running:
            self.process_events(pygame.event.get())
            self.draw(window)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("width", type=int)
    parser.add_argument("height", type=int)
    parser.add_argument("path", type=str)

    args = parser.parse_args()

    editor = Editor(args.width, args.height, args.path)

    editor.mainloop()
