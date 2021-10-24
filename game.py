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
from game_map import MapHelper, MapCell, Map
from player import Player
from utility import rotation_matrix
from data_manager import DataManager, Texture
from vector import Vector2
# typing
from typing import Callable, Union

# typing types
ColourType = Union[Color, Color, str, tuple[int, int, int], list[int], int, tuple[int, int, int, int]],


class RaycastInfo:
    def __init__(self, hit: bool, perp_wall_dist: float, collision: Vector2, ns_wall: bool, map_position: tuple[int, int]):
        self.hit = hit
        self.perp_wall_dist: float = perp_wall_dist
        self.collision: Vector2 = collision
        self.ns_wall: bool = ns_wall
        self.map_position: tuple[int, int] = map_position


class RaycastingGame:
    class DrawMode(Enum):
        GAME = 0
        MAP = 1

    MOUSE_SPEED_FACTOR = 0.003

    DrawMethod = Callable[[Surface], None]

    def __init__(self, data: DataManager):
        self.data: DataManager = data

        self.background_colour: ColourType = (255, 255, 255)
        self.clock: Clock = Clock()
        self.running: bool = False
        self.draw_mode: RaycastingGame.DrawMode = RaycastingGame.DrawMode.GAME
        self.draw_mode_map: dict[RaycastingGame.DrawMode, RaycastingGame.DrawMethod] = {
            RaycastingGame.DrawMode.GAME: self.draw_game,
            RaycastingGame.DrawMode.MAP: self.draw_map,
        }
        self.map_colour_map: dict[MapCell, ColourType] = {
            MapCell.EMPTY: (0, 0, 0),
            MapCell.WALL: (255, 0, 0),
        }
        self.texture_map: dict[MapCell, Texture] = {
            MapCell.WALL: data.textures["mossy_cobblestone"]
        }
        self.map: Map = MapHelper.generate_random_map((16, 16))  # TODO: map selection
        self.map = self.data.maps["map"]
        self.game_dim = (self.map.shape[1], self.map.shape[0])
        self.player: Player = Player(
            self.data.config,
            self,
            position=np.array(self.game_dim, dtype=float) / 2,
        )
        self.key_map: dict[int, Callable[[Event], None]] = {
            pygame.K_ESCAPE: self.on_quit,
            pygame.K_m: self.on_toggle_map,
        }

    def on_quit(self, event: Event):
        self.running = False

    def on_toggle_map(self, event: Event):
        if event.type == pygame.KEYUP:
            return
        if self.draw_mode == RaycastingGame.DrawMode.GAME:
            self.draw_mode = RaycastingGame.DrawMode.MAP
        elif self.draw_mode == RaycastingGame.DrawMode.MAP:
            self.draw_mode = RaycastingGame.DrawMode.GAME

    def process_events(self, events: list[Event]):
        for event in events:
            if event.type == pygame.KEYDOWN or event.type == pygame.KEYUP:
                if event.key in self.key_map.keys():
                    self.key_map[event.key](event)
            elif event.type == pygame.MOUSEMOTION:
                self.player.rotate(rotation_matrix(-event.rel[0] * RaycastingGame.MOUSE_SPEED_FACTOR * self.data.config.getfloat("Input", "mouse_sensitivity")))

    def update(self, delta_time: float):
        self.process_events(pygame.event.get())
        self.player.update(delta_time)

    def draw(self, surface: Surface):
        surface.fill(self.background_colour)
        self.draw_mode_map[self.draw_mode](surface)

    def draw_map(self, surface: Surface):
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

    def raycast(self, origin: Vector2, direction: Vector2) -> RaycastInfo:
        # from https://lodev.org/cgtutor/raycasting.html

        map_x = int(origin[0])
        map_y = int(origin[1])

        delta_dist_x = np.inf if direction[0] == 0 else abs(1 / direction[0])
        delta_dist_y = np.inf if direction[1] == 0 else abs(1 / direction[1])

        if direction[0] < 0:
            step_x = -1
            side_dist_x = delta_dist_x * (origin[0] - map_x)
        else:
            step_x = 1
            side_dist_x = delta_dist_x * (map_x + 1 - origin[0])
        if direction[1] < 0:
            step_y = -1
            side_dist_y = delta_dist_y * (origin[1] - map_y)
        else:
            step_y = 1
            side_dist_y = delta_dist_y * (map_y + 1 - origin[1])

        hit = False
        ns_wall = True

        while not hit:
            if side_dist_x < side_dist_y:
                side_dist_x += delta_dist_x
                map_x += step_x
                ns_wall = True
            else:
                side_dist_y += delta_dist_y
                map_y += step_y
                ns_wall = False

            if map_x < 0 or map_x >= self.map.shape[1] or map_y < 0 or map_y >= self.map.shape[0]:
                return RaycastInfo(False, np.inf, np.array([np.inf, np.inf], dtype=float), ns_wall, (map_x, map_y))

            hit = self.map[map_y, map_x] != 0

        if ns_wall:
            perp_wall_dist = side_dist_x - delta_dist_x
        else:
            perp_wall_dist = side_dist_y - delta_dist_y

        return RaycastInfo(True, perp_wall_dist, origin + direction * perp_wall_dist, ns_wall, (map_x, map_y))

    def draw_game(self, surface: Surface):
        pixel_array = pygame.PixelArray(surface)

        for x in range(surface.get_width()):
            camera_x = x / surface.get_width() - 0.5
            info = self.raycast(self.player.position, self.player.forward + self.player.camera_plane * camera_x)

            if info.hit:
                line_height = surface.get_height() if info.perp_wall_dist < 1 else int(surface.get_height() / info.perp_wall_dist)

                wall_x = info.collision[1] if info.ns_wall else info.collision[0]
                wall_x -= np.floor(wall_x)

                texture = self.texture_map[self.map[info.map_position[1], info.map_position[0]]]

                texture_x = int(wall_x * texture.shape[0])

                centre_offset_y = (surface.get_height() - line_height) / 2

                for y in range(min(surface.get_height(), line_height)):
                    pixel_array[x, int(y + centre_offset_y)] = texture[texture_x, int(y / line_height * (texture.shape[1] - 1))]

    def mainloop(self):
        window = pygame.display.set_mode((0, 0))

        pygame.mouse.set_visible(False)
        pygame.event.set_grab(True)

        self.running = True

        while self.running:
            self.update(self.clock.tick() / 1000)
            self.draw(window)
            pygame.display.flip()
