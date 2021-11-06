from __future__ import annotations

# pygame
import pygame
from pygame.event import Event
from pygame import Surface
# numpy
import numpy as np
# project
from game_map import MapCell
from data_manager import Texture
from sprite import Sprite
# typing
from typing import TYPE_CHECKING
from numpy_typing import NDArray

if TYPE_CHECKING:
    from game import RaycastingGame


class GameRenderer:
    RAY_DISTANCE_BOUND: float = 0.01

    def __init__(self, game: RaycastingGame):
        self.game: RaycastingGame = game
        self.texture_map: dict[MapCell, list[Texture]] = {
            MapCell.WALL: self.game.data.texture_columns["mossy_cobblestone"]
        }
        self.z_buffer: [NDArray[float]] = np.empty((0, ))

    def resize(self, size):
        self.z_buffer = np.empty((size[0], ))

    def draw_walls(self, surface: Surface):
        for x in range(surface.get_width()):
            # how far x is along the screen between -0.5 and 0.5
            camera_x = x / surface.get_width() - 0.5
            # raycast
            info = self.game.raycast(self.game.player.position, self.game.player.forward + self.game.player.camera_plane * camera_x)

            # store hit distance into z-buffer
            self.z_buffer[x] = info.perp_wall_dist

            if info.hit:
                # determine line height, clamping to surface height if the wall distance is very low to avoid running
                # out of memory when scaling the texture
                line_height = surface.get_height() if info.perp_wall_dist <= GameRenderer.RAY_DISTANCE_BOUND else int(surface.get_height() / info.perp_wall_dist)

                # find the point at which the wall was hit
                wall_x = info.collision[1] if info.ns_wall else info.collision[0]
                wall_x -= np.floor(wall_x)

                # get the wall's texture columns from the texture map
                texture = self.texture_map[self.game.map[info.map_position[1], info.map_position[0]]]

                # find the index of the texture column the ray hit
                texture_x = int(wall_x * len(texture))

                # find the
                centre_offset_y = (surface.get_height() - line_height) / 2

                # blit scaled texture column to screen
                surface.blit(pygame.transform.scale(texture[texture_x], (1, line_height)), (x, centre_offset_y))

    def draw_sprites(self, surface: Surface):
        def square_distance(sprite: Sprite):
            relative_position = sprite.position - self.game.player.position
            return relative_position[0] * relative_position[0] + relative_position[1] * relative_position[1]

        sorted_sprites = sorted(self.game.sprites, key=square_distance, reverse=True)

        # determine surface centres on each axis
        screen_centre_x = surface.get_width() / 2
        screen_centre_y = surface.get_height() / 2

        for sprite in sorted_sprites:
            texture = sprite.texture
            # find position of sprite with player as the origin
            relative_position = sprite.position - self.game.player.position
            # rotate sprite to camera space
            transformed = np.matmul(self.game.player.inv_camera_matrix, relative_position)

            # determine sprite dimensions based on distance
            sprite_height = min(surface.get_height() * texture.get_height(), abs(int(surface.get_height() / transformed[1])))
            sprite_width = int(texture.get_width() / texture.get_height() * sprite_height)

            # determine centre of sprite on screen
            screen_x = screen_centre_x * (1 + transformed[0] / transformed[1] * 2) - sprite_width / 2
            screen_y = screen_centre_y - sprite_height / 2
            # surface.blit(pygame.transform.scale(texture, (sprite_width, sprite_height)), (screen_x, screen_y))

            # scale texture columns to the correct size
            scaled_texture_columns = list(map(lambda x: pygame.transform.scale(x, (1, sprite_height)), sprite.texture_columns))

            for x in range(sprite_width):
                column_screen_x = int(screen_x + x)
                # if:
                # 1. the distance to the sprite is not negative (i.e. it is in front of the camera)
                # 2. the texture column is on screen
                # 3. the texture column is in front of all walls
                if transformed[1] > 0 and \
                        0 < column_screen_x < self.z_buffer.shape[0] and \
                        transformed[1] < self.z_buffer[column_screen_x]:
                    surface.blit(scaled_texture_columns[int(x / sprite_width * texture.get_width())], (column_screen_x, screen_y))

    def draw(self, surface: Surface):
        self.draw_walls(surface)
        self.draw_sprites(surface)
