# pygame
import pygame
from pygame.event import Event
from pygame.time import Clock
from pygame.surface import Surface
# numpy
import numpy as np
# numba
import numba
# standard
from enum import Enum
import logging
# project
from player import Player
from game_map import Map
from data_manager import DataManager
from utility import rotation_matrix
from vector import Vector2
from map_renderer import MapRenderer
from game_renderer import GameRenderer
from ui_renderer import UIRenderer
from sprite import Sprite
from game_object import GameObject
from rat import Rat
from skeleton import Skeleton
from enemy import Enemy
from enemy_manager import EnemyManager
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
def raycast(origin_x: float, origin_y: float, direction_x: float, direction_y: float, game_map: Map, distance: float = np.inf):
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

        if ns_wall and side_dist_x - delta_dist_x > distance or not ns_wall and side_dist_y - delta_dist_y > distance:
            return False, None, None, None, None

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


game_logger = logging.getLogger("game")


class RaycastingGame:
    class DrawMode(Enum):
        GAME = 0
        MAP = 1
        TITLE = 2
        GAMEOVER = 3

    class GameMode(Enum):
        UI = 0
        GAME = 1

    MOUSE_SPEED_FACTOR = 0.005
    WINDOW_TITLE: str = "Necrom"

    DrawMethod = Callable[[Surface], None]
    UpdateMethod = Callable[[float], None]
    EventAction = Callable[[Event], None]

    def __init__(self, data: DataManager):
        self.data: DataManager = data

        self.clock: Clock = Clock()
        self.running: bool = False
        self.map: Map = self.data.maps["main"]
        self.player: Player = Player(
            self.data.config,
            self,
            position=np.array(self.map.shape, dtype=float) / 1.5,
        )
        self.sprites: list[Sprite] = []
        self.game_objects: list[GameObject] = []
        self.enemies: list[Enemy] = []
        Rat(np.array([5.5, 5.5], dtype=float), self).bind(self)
        Rat(np.array([2.5, 2.5], dtype=float), self).bind(self)
        Rat(np.array([11.5, 14.5], dtype=float), self).bind(self)
        self.map_renderer: MapRenderer = MapRenderer(self.map, self.player, self.sprites)
        self.game_renderer: GameRenderer = GameRenderer(self, self.data.textures["dusk-sky"].texture)
        self.ui_renderer: UIRenderer = UIRenderer(self)
        self.enemy_manager: EnemyManager = self.create_enemy_manager()
        self.game_mode: RaycastingGame.GameMode = RaycastingGame.GameMode.UI
        self.update_mode_map: dict[RaycastingGame.GameMode, RaycastingGame.UpdateMethod] = {
            RaycastingGame.GameMode.GAME: self.update_game,
            RaycastingGame.GameMode.UI: self.update_ui,
        }
        self.draw_mode: RaycastingGame.DrawMode = RaycastingGame.DrawMode.TITLE
        self.draw_mode_map: dict[RaycastingGame.DrawMode, RaycastingGame.DrawMethod] = {
            RaycastingGame.DrawMode.GAME: self.game_renderer.draw,
            RaycastingGame.DrawMode.MAP: self.map_renderer.draw,
            RaycastingGame.DrawMode.TITLE: self.ui_renderer.draw_title,
            RaycastingGame.DrawMode.GAMEOVER: self.ui_renderer.draw_gameover,
        }
        self.key_map: dict[int, RaycastingGame.EventAction] = {
            pygame.K_ESCAPE: self.handle_quit,
            pygame.K_m: self.handle_toggle_map,
        }
        self.needs_resize: bool = False

    def create_enemy_manager(self) -> EnemyManager:
        empty_position = np.empty((2, ), dtype=float)
        waves = [
            [
                Skeleton(empty_position, self),
                Skeleton(empty_position, self),
                Skeleton(empty_position, self)
            ],
            [
                Skeleton(empty_position, self),
                Skeleton(empty_position, self),
                Skeleton(empty_position, self)
            ]
        ]
        spawn_locations = [
            np.array([2.5, 2.5], dtype=float),
            np.array([9.5, 1.5], dtype=float),
            np.array([13.5, 3.5], dtype=float),
            np.array([2.5, 13.5], dtype=float),
            np.array([11.5, 14.5], dtype=float),
        ]
        return EnemyManager(self, spawn_locations, waves)

    def start_game(self):
        self.player: Player = Player(
            self.data.config,
            self,
            position=np.array(self.map.shape, dtype=float) / 1.5,
        )
        self.sprites: list[Sprite] = []
        self.game_objects: list[GameObject] = []
        self.enemies: list[Enemy] = []
        Rat(np.array([5.5, 5.5], dtype=float), self).bind(self)
        Rat(np.array([2.5, 2.5], dtype=float), self).bind(self)
        Rat(np.array([11.5, 14.5], dtype=float), self).bind(self)
        self.map_renderer.player = self.player
        self.map_renderer.sprites = self.sprites
        self.enemy_manager: EnemyManager = self.create_enemy_manager()
        self.game_mode_game()

    def game_over(self):
        self.game_mode_ui()
        self.draw_mode = RaycastingGame.DrawMode.GAMEOVER

    def quit(self):
        self.running = False
        self.data.save_config()

    def handle_quit(self, event: Event):
        if event.type == pygame.KEYUP:
            return
        escape_behaviour = self.data.config.get("Behaviour", "escape_behaviour")
        if escape_behaviour == "quit":
            self.quit()
        elif escape_behaviour == "unlock mouse":
            pygame.mouse.set_visible(True)
            pygame.event.set_grab(False)
        else:
            game_logger.warning("Escape behaviour configuration not recognised. Defaulting to quit.")
            self.quit()

    def handle_toggle_map(self, event: Event):
        if event.type == pygame.KEYUP:
            return
        if self.draw_mode == RaycastingGame.DrawMode.GAME:
            self.draw_mode = RaycastingGame.DrawMode.MAP
        elif self.draw_mode == RaycastingGame.DrawMode.MAP:
            self.draw_mode = RaycastingGame.DrawMode.GAME

    def process_game_events(self, events: list[Event]):
        for event in events:
            if event.type == pygame.KEYDOWN or event.type == pygame.KEYUP:
                if event.key in self.key_map.keys():
                    self.key_map[event.key](event)
            elif event.type == pygame.MOUSEMOTION:
                self.player.rotate(rotation_matrix(event.rel[0] * RaycastingGame.MOUSE_SPEED_FACTOR * self.data.config.getfloat("Input", "mouse_sensitivity")))
            elif event.type == pygame.VIDEORESIZE:
                self.resize(event.size)
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == pygame.BUTTON_LEFT:
                    self.player.attack()

    def process_ui_events(self, events: list[Event]):
        for event in events:
            if event.type == pygame.MOUSEMOTION:
                self.ui_renderer.update_mouse(event.pos)
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == pygame.BUTTON_LEFT:
                    self.ui_renderer.handle_click()
            elif event.type == pygame.VIDEORESIZE:
                self.resize(event.size)

    def resize(self, size):
        self.game_renderer.resize(size)
        self.ui_renderer.resize(size)

    def raycast(self, origin: Vector2, direction: Vector2, distance: float = np.inf) -> RaycastInfo:
        return RaycastInfo(*raycast(origin[0], origin[1], direction[0], direction[1], self.map, distance))

    def update_game(self, delta_time: float):
        self.process_game_events(pygame.event.get())
        self.player.update(delta_time)
        self.enemy_manager.update(delta_time)
        for obj in self.game_objects:
            obj.update(delta_time)

    def update_ui(self, delta_time: float):
        self.process_ui_events(pygame.event.get())

    def update(self, delta_time: float):
        self.update_mode_map[self.game_mode](delta_time)

    def draw(self, surface: Surface):
        self.draw_mode_map[self.draw_mode](surface)

    def init_window(self) -> pygame.Surface:
        video_config = self.data.config["Video"]
        if video_config.getboolean("fullscreen"):
            flags = pygame.FULLSCREEN
            if video_config.getboolean("scaled"):
                window = pygame.display.set_mode((video_config.getint("width"), video_config.getint("height")), flags=flags | pygame.SCALED)
            else:
                window = pygame.display.set_mode((0, 0), flags=flags)
        else:
            window = pygame.display.set_mode((video_config.getint("width"), video_config.getint("height")))

        pygame.display.set_caption(RaycastingGame.WINDOW_TITLE)

        return window

    def game_mode_game(self):
        self.game_mode = RaycastingGame.GameMode.GAME
        self.draw_mode = RaycastingGame.DrawMode.GAME
        pygame.mouse.set_visible(False)
        pygame.event.set_grab(True)

    def game_mode_ui(self):
        self.game_mode = RaycastingGame.GameMode.UI
        pygame.mouse.set_visible(True)
        pygame.event.set_grab(False)

    def mainloop(self):
        window = self.init_window()

        self.resize(window.get_size())

        self.running = True

        self.game_mode_ui()

        self.enemy_manager.start()

        while self.running:
            self.update(self.clock.tick() / 1000)
            if self.needs_resize:
                self.resize(window.get_size())
                self.needs_resize = False
            self.draw(window)
            pygame.display.flip()
