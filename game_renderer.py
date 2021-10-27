from __future__ import annotations

# pygame
import pygame
from pygame import Surface
# numpy
import numpy as np
# project
from player import Player
from game_map import MapCell
from data_manager import Texture
# typing
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from game import RaycastingGame


class GameRenderer:
    def __init__(self, game: RaycastingGame):
        self.game: RaycastingGame = game
        self.texture_map: dict[MapCell, Texture] = {
            MapCell.WALL: self.game.data.textures["mossy_cobblestone"]
        }

    def draw(self, surface: Surface):
        for x in range(surface.get_width()):
            camera_x = x / surface.get_width() - 0.5
            info = self.game.raycast(self.game.player.position, self.game.player.forward + self.game.player.camera_plane * camera_x)

            if info.hit:
                line_height = surface.get_height() if info.perp_wall_dist <= 0.01 else int(surface.get_height() / info.perp_wall_dist)

                wall_x = info.collision[1] if info.ns_wall else info.collision[0]
                wall_x -= np.floor(wall_x)

                texture = self.texture_map[self.game.map[info.map_position[1], info.map_position[0]]]

                texture_x = int(wall_x * len(texture))

                centre_offset_y = (surface.get_height() - line_height) / 2

                surface.blit(pygame.transform.scale(texture[texture_x], (1, line_height)), (x, centre_offset_y))