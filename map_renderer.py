# project
from game_map import Map, MapCell
from player import Player
from colour import ColourType
from sprite import Sprite
from vector import Vector2
# pygame
import pygame
from pygame import Surface
# numpy
import numpy as np


class MapRenderer:
    BACKGROUND_COLOUR: ColourType = (255, 255, 255)

    def __init__(self, game_map: Map, player: Player, sprites: list[Sprite]):
        self.map: Map = game_map
        self.player: Player = player
        self.sprites: list[Sprite] = sprites
        self.map_colour_map: dict[MapCell, ColourType] = {
            MapCell.EMPTY: (0, 0, 0),
            MapCell.WALL: (255, 0, 0),
        }
        self.ray_colour: ColourType = (0, 255, 0)
        self.ray_width: int = 3

    def draw_ray(self, surface: Surface, origin: Vector2, direction: Vector2):
        pygame.draw.line(surface, self.ray_colour, origin, origin + direction * surface.get_width(), width=self.ray_width)

    def draw(self, surface: Surface):
        surface.fill(MapRenderer.BACKGROUND_COLOUR)
        # draw map
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

        # draw player
        player_position = self.player.position / self.map.shape[0] * surface.get_height() + centre_offset

        pygame.draw.circle(surface, (0, 255, 0), player_position, 5)
        # TODO add more rays and use z-buffer to constrain them
        self.draw_ray(surface, player_position, self.player.forward + self.player.camera_plane * -0.5)
        self.draw_ray(surface, player_position, self.player.forward + self.player.camera_plane * 0.5)

        # draw sprites
        for sprite in self.sprites:
            texture = sprite.textures[0].texture
            surface.blit(texture, centre_offset + sprite.position * cell_width - (texture.get_width() / 2, texture.get_height() / 2))
