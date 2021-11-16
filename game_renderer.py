from __future__ import annotations

# pygame
import pygame
from pygame import Surface
from pygame.freetype import SysFont
# numpy
import numpy as np
from numpy_typing import NDArray
# project
from game_map import MapCell
from data_manager import Texture
from sprite import Sprite
from colour import ColourType
from health_bar import HealthBar
# standard
from typing import TYPE_CHECKING
import math

if TYPE_CHECKING:
    from game import RaycastingGame


class GameRenderer:
    RAY_DISTANCE_BOUND: float = 0.01
    FONT_SCALE_RATIO: float = 0.05
    FONT_NAME: str = ""
    HIT_EFFECT_TIME: int = 1000
    HIT_EFFECT_MAX_OPACITY = 150

    def __init__(self, game: RaycastingGame, sky_texture: Texture):
        self.game: RaycastingGame = game
        self.texture_map: dict[MapCell, list[Texture]] = {
            MapCell.WALL: self.game.data.textures["mossy_cobblestone"].columns
        }
        self.z_buffer: [NDArray[float]] = np.empty((0, ))
        self.floor_colour: ColourType = (75, 105, 47)
        self.sky_texture: Texture = sky_texture
        self.scaled_sky: Texture = sky_texture
        self.light_surface: Surface = Surface((0, 0))
        self.light_surface.set_alpha(100)
        self.hit_surface: Surface = Surface((0, 0))
        self._hit_start_time: int = np.iinfo(int).min
        self.font: SysFont = SysFont(GameRenderer.FONT_NAME, 0)
        self.health_bar: HealthBar = HealthBar(self.game.data)

    def resize(self, size):
        self.z_buffer = np.empty((size[0], ))

        # resize light surface
        old_colour = (0, 0, 0) if self.light_surface.get_width() == 0 or self.light_surface.get_height() == 0 else self.light_surface.get_at((0, 0))
        old_alpha = self.light_surface.get_alpha()
        self.light_surface = Surface(size)
        self.light_surface.fill(old_colour)
        self.light_surface.set_alpha(old_alpha)

        old_alpha = self.light_surface.get_alpha()
        self.hit_surface = Surface(size)
        self.hit_surface.set_alpha(old_alpha)
        self.hit_surface.fill((255, 0, 0))

        # scale sky texture
        texture_height = size[1] // 2
        texture_width = texture_height * self.sky_texture.get_width() // self.sky_texture.get_height()
        if texture_width < size[0]:  # width is too small
            texture_width = size[0]
            texture_height = texture_width * self.sky_texture.get_height() // self.sky_texture.get_width()

        self.scaled_sky = pygame.transform.scale(self.sky_texture, (texture_width, texture_height))

        # font
        self.font: SysFont = SysFont(GameRenderer.FONT_NAME, int(size[1] * GameRenderer.FONT_SCALE_RATIO))

        # health bar
        self.health_bar.resize(size)

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

                centre_offset_y = (surface.get_height() - line_height) / 2

                scaled_texture = pygame.transform.scale(texture[texture_x], (1, line_height))

                # blit scaled texture column to screen
                surface.blit(scaled_texture, (x, centre_offset_y))

    def draw_sprites(self, surface: Surface):
        def square_distance(sprite: Sprite):
            relative_position = sprite.position - self.game.player.position
            return relative_position[0] * relative_position[0] + relative_position[1] * relative_position[1]

        sorted_sprites = sorted(self.game.sprites, key=square_distance, reverse=True)

        # determine surface centres on each axis
        screen_centre_x = surface.get_width() / 2
        screen_centre_y = surface.get_height() / 2

        for sprite in sorted_sprites:
            # find position of sprite with player as the origin
            relative_position = sprite.position - self.game.player.position
            # rotate sprite to camera space
            transformed = np.matmul(self.game.player.inv_camera_matrix, relative_position)

            for texture_data in sprite.textures:
                if texture_data is None:
                    continue

                texture = texture_data.texture
                # determine sprite dimensions based on distance
                sprite_height = min(surface.get_height() * texture.get_height(), abs(int(surface.get_height() / transformed[1] * sprite.scale)))
                sprite_width = int(sprite_height * texture.get_width() / texture.get_height())

                # determine centre of sprite on screen
                screen_x = screen_centre_x * (1 + transformed[0] / transformed[1] * 2) - sprite_width / 2
                screen_y = screen_centre_y - sprite_height / 2 + surface.get_height() * -sprite.height_offset / transformed[1]

                if texture_data.simple_clip:
                    flipped_texture = pygame.transform.flip(texture, texture_data.flip_x, False) if texture_data.flip_x else texture
                    surface.blit(pygame.transform.scale(flipped_texture, (sprite_width, sprite_height)), (screen_x, screen_y))
                else:
                    # scale texture columns to the correct size
                    scaled_texture_columns = list(map(lambda x: pygame.transform.scale(x, (1, sprite_height)), texture_data.columns))

                    for x in range(sprite_width):
                        column_screen_x = int(screen_x + x)
                        # if:
                        # 1. the distance to the sprite is not negative (i.e. it is in front of the camera)
                        # 2. the texture column is on screen
                        # 3. the texture column is in front of all walls
                        if transformed[1] > 0 and \
                                0 <= column_screen_x < self.z_buffer.shape[0] and \
                                transformed[1] < self.z_buffer[column_screen_x]:
                            index = int(x / sprite_width * texture.get_width())
                            if texture_data.flip_x:
                                index = -index
                            surface.blit(scaled_texture_columns[index], (column_screen_x, screen_y))

    def draw_floor(self, surface: Surface):
        surface.fill(self.floor_colour, (0, surface.get_height() // 2, surface.get_width(), surface.get_height()))

    def draw_sky(self, surface: Surface):
        sky_region = math.atan2(self.game.player.forward[1], self.game.player.forward[0]) / math.pi / 2
        if sky_region < 0:
            sky_region = 1 + sky_region

        half_surface_height = surface.get_height() // 2

        source = pygame.Rect(int(self.scaled_sky.get_width() * sky_region), 0, surface.get_width(), half_surface_height)

        surface.blit(self.scaled_sky, (0, 0), source)

        if source.right > self.scaled_sky.get_width():
            dest = (self.scaled_sky.get_width() - source.left, 0)
            surface.blit(self.scaled_sky, dest, pygame.Rect(0, 0, source.left, half_surface_height))

    def postprocess(self, surface: Surface):
        surface.blit(self.light_surface, (0, 0))

        time = pygame.time.get_ticks()
        hit_effect_interval = time - self._hit_start_time
        if hit_effect_interval < self.HIT_EFFECT_TIME:
            effect_factor = hit_effect_interval / self.HIT_EFFECT_TIME

            self.hit_surface.set_alpha(GameRenderer.HIT_EFFECT_MAX_OPACITY - int(effect_factor * GameRenderer.HIT_EFFECT_MAX_OPACITY))

            surface.blit(self.hit_surface, (0, 0))

    def draw_weapon(self, surface: Surface):
        texture = self.game.player.weapon.get_texture().texture
        height = surface.get_height() * self.game.player.weapon.get_window_scale()
        width = height * texture.get_width() / texture.get_height()
        scaled_texture = pygame.transform.scale(texture, (int(width), int(height)))

        screen_x = (surface.get_width() - scaled_texture.get_width()) // 2
        screen_y = surface.get_height() - scaled_texture.get_height()

        surface.blit(scaled_texture, (screen_x, screen_y))

    def draw_gui(self, surface: Surface):
        self.health_bar.draw(surface, (0, self.font.size), self.game.player)

    def draw(self, surface: Surface):
        self.draw_floor(surface)
        self.draw_sky(surface)
        self.draw_walls(surface)
        self.draw_sprites(surface)
        self.postprocess(surface)
        self.draw_weapon(surface)
        self.draw_gui(surface)

    def run_hit_effect(self):
        self._hit_start_time = pygame.time.get_ticks()
