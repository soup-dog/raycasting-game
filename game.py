# pygame
import pygame
from pygame.event import Event
from pygame.time import Clock
from pygame.surface import Surface
from pygame import Color
# numpy
import numpy as np
# numba
import numba
# standard
from enum import Enum
# project
from player import Player
from game_map import MapCell, Map
from data_manager import DataManager, Texture
from utility import rotation_matrix
from vector import Vector2
from map_renderer import MapRenderer
from game_renderer import GameRenderer
from colour import ColourType
# typing
from typing import Callable


class RaycastInfo:
    def __init__(self, hit: bool, perp_wall_dist: float, collision: Vector2, ns_wall: bool, map_position: tuple[int, int]):
        self.hit = hit
        self.perp_wall_dist: float = perp_wall_dist
        self.collision: Vector2 = collision
        self.ns_wall: bool = ns_wall
        self.map_position: tuple[int, int] = map_position


@numba.jit(nopython=True)
def raycast(origin_x: float, origin_y: float, direction_x: float, direction_y: float, game_map: Map):
    # from https://lodev.org/cgtutor/raycasting.html

    map_x = int(origin_x)
    map_y = int(origin_y)

    delta_dist_x = np.inf if direction_x == 0 else abs(1 / direction_x)
    delta_dist_y = np.inf if direction_y == 0 else abs(1 / direction_y)

    if direction_x < 0:
        step_x = -1
        side_dist_x = delta_dist_x * (origin_x - map_x)
    else:
        step_x = 1
        side_dist_x = delta_dist_x * (map_x + 1 - origin_x)
    if direction_y < 0:
        step_y = -1
        side_dist_y = delta_dist_y * (origin_y - map_y)
    else:
        step_y = 1
        side_dist_y = delta_dist_y * (map_y + 1 - origin_y)

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

        if map_x < 0 or map_x >= game_map.shape[1] or map_y < 0 or map_y >= game_map.shape[0]:
            return False, np.inf, (np.inf, np.inf), ns_wall, (map_x, map_y)

        hit = game_map[map_y, map_x] != 0

    if ns_wall:
        perp_wall_dist = side_dist_x - delta_dist_x
    else:
        perp_wall_dist = side_dist_y - delta_dist_y

    return (True,
            perp_wall_dist,
            (origin_x + direction_x * perp_wall_dist, origin_y + direction_y * perp_wall_dist),
            ns_wall,
            (map_x, map_y))


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
        self.map: Map = self.data.maps["map"]
        self.game_dim = (self.map.shape[1], self.map.shape[0])
        self.player: Player = Player(
            self.data.config,
            self,
            position=np.array(self.game_dim, dtype=float) / 2,
        )
        self.map_renderer: MapRenderer = MapRenderer(self.map, self.player)
        self.game_renderer: GameRenderer = GameRenderer(self)
        self.draw_mode: RaycastingGame.DrawMode = RaycastingGame.DrawMode.GAME
        self.draw_mode_map: dict[RaycastingGame.DrawMode, RaycastingGame.DrawMethod] = {
            RaycastingGame.DrawMode.GAME: self.game_renderer.draw,
            RaycastingGame.DrawMode.MAP: self.map_renderer.draw,
        }
        self.key_map: dict[int, Callable[[Event], None]] = {
            pygame.K_ESCAPE: self.on_quit,
            pygame.K_m: self.on_toggle_map,
        }

    def on_quit(self, event: Event):
        if event.type == pygame.KEYUP:
            return
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

    def raycast(self, origin: Vector2, direction: Vector2) -> RaycastInfo:
        return RaycastInfo(*raycast(origin[0], origin[1], direction[0], direction[1], self.map))

    def update(self, delta_time: float):
        self.process_events(pygame.event.get())
        self.player.update(delta_time)

    def draw(self, surface: Surface):
        surface.fill(self.background_colour)
        self.draw_mode_map[self.draw_mode](surface)

    def mainloop(self):
        # window = pygame.display.set_mode((750, 500), flags=pygame.FULLSCREEN | pygame.SCALED)
        window = pygame.display.set_mode((0, 0))

        pygame.mouse.set_visible(False)
        pygame.event.set_grab(True)

        self.running = True

        while self.running:
            self.update(self.clock.tick() / 1000)
            self.draw(window)
            pygame.display.flip()
