# project
from game_map import Map, MapCell
from player import Player
from colour import ColourType
# pygame
import pygame
from pygame import Surface
# numpy
import numpy as np


class MapRenderer:
    def __init__(self, game_map: Map, player: Player):
        self.map = game_map
        self.player = player
        self.map_colour_map: dict[MapCell, ColourType] = {
            MapCell.EMPTY: (0, 0, 0),
            MapCell.WALL: (255, 0, 0),
        }

    def draw(self, surface: Surface):
        cell_height = int(surface.get_height() / self.map.shape[0])
        cell_width = cell_height

        centre_offset_x = (surface.get_width() - cell_width * self.map.shape[0]) / 2
        centre_offset_y = (surface.get_height() - cell_height * self.map.shape[1]) / 2
        centre_offset = np.array([centre_offset_x, centre_offset_y])

        for row in range(self.map.shape[0]):
            for col in range(self.map.shape[1]):
                colour = self.map_colour_map[self.map[row, col]]
                rect = (
                    col * cell_width + centre_offset_x,
                    row * cell_height + centre_offset_y,
                    cell_width,
                    cell_height
                )
                pygame.draw.rect(surface, colour, rect)

        player_position = self.player.position / self.map.shape[0] * surface.get_height() + centre_offset

        pygame.draw.circle(surface, (0, 255, 0), player_position, 5)
        pygame.draw.line(surface, (0, 255, 0), player_position, player_position + self.player.forward * surface.get_width(), width=3)
