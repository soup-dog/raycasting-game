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
from game_map import MapHelper, MapCell
from player import Player
from utility import rotation_matrix
# typing
from typing import Callable, Union
from numpy.typing import NDArray

pygame.init()


ColourType = Union[Color, Color, str, tuple[int, int, int], list[int], int, tuple[int, int, int, int]],
Vector2 = NDArray[float]


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
            pygame.K_ESCAPE: self.quit,
            pygame.K_m: self.toggle_map,
        }
        self.draw_mode: RaycastingGame.DrawMode = RaycastingGame.DrawMode.GAME
        self.draw_mode_map: dict[RaycastingGame.DrawMode, RaycastingGame.DrawMethod] = {
            RaycastingGame.DrawMode.GAME: self.draw_game,
            RaycastingGame.DrawMode.MAP: self.draw_map,
        }
        self.map_colour_map: dict[MapCell, ColourType] = {
            MapCell.EMPTY: (0, 0, 0),
            MapCell.WALL: (255, 0, 0),
        }
        self.map: NDArray[np.uint8] = MapHelper.generate_random_map((16, 16))
        self.game_dim = (self.map.shape[1], self.map.shape[0])
        self.player: Player = Player(np.array(self.game_dim, dtype=float) / 2, np.array([1, 0], dtype=float))

    def quit(self):
        self.running = False

    def toggle_map(self):
        if self.draw_mode == RaycastingGame.DrawMode.GAME:
            self.draw_mode = RaycastingGame.DrawMode.MAP
        elif self.draw_mode == RaycastingGame.DrawMode.MAP:
            self.draw_mode = RaycastingGame.DrawMode.GAME

    def process_events(self, events: list[Event]):
        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key in self.key_map.keys():
                    self.key_map[event.key]()
            elif event.type == pygame.MOUSEMOTION:
                self.player.rotate(rotation_matrix(-event.rel[0] / 700))

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
        pygame.draw.line(surface, (0, 255, 0), player_position, player_position + self.player.direction * surface.get_width(), width=3)

    def raycast(self, origin: Vector2, direction: Vector2) -> (bool, float):
        # from https://lodev.org/cgtutor/raycasting.html

        map_x = int(origin[0])
        map_y = int(origin[1])

        delta_dist_x = float("inf") if direction[0] == 0 else abs(1 / direction[0])
        delta_dist_y = float("inf") if direction[1] == 0 else abs(1 / direction[1])

        if direction[0] < 0:
            step_x = -1
            side_dist_x = (origin[0] - map_x) * delta_dist_x
        else:
            step_x = 1
            side_dist_x = (map_x + 1 - origin[0]) * delta_dist_x
        if direction[1] < 0:
            step_y = -1
            side_dist_y = (origin[1] - map_y) * delta_dist_y
        else:
            step_y = 1
            side_dist_y = (map_y + 1 - origin[1] * delta_dist_y)

        hit = False
        side = 0

        while not hit:
            if side_dist_x < side_dist_y:
                side_dist_x += delta_dist_x
                map_x += step_x
                side = 0
            else:
                side_dist_y += delta_dist_y
                map_y += step_y
                side = 1

            if map_x < 0 or map_x >= self.map.shape[1] or map_y < 0 or map_y >= self.map.shape[0]:
                return False, float("inf")

            hit = self.map[map_x, map_y] != 0

        if side == 0:
            perp_wall_dist = side_dist_x - delta_dist_x
        else:
            perp_wall_dist = side_dist_y - delta_dist_y

        return True, perp_wall_dist

    def draw_game(self, surface: Surface):
        for x in range(surface.get_width()):
            camera_x = x / surface.get_width() - 0.5
            hit, perpendicular_distance = self.raycast(self.player.position, self.player.direction + self.player.camera_plane * camera_x)

            line_height = surface.get_height() if perpendicular_distance == 0 else int(surface.get_height() / perpendicular_distance)

            centre_offset_y = surface.get_height() / 2

            pygame.draw.line(
                surface,
                (0, 255, 0),
                (x, -line_height / 2 + centre_offset_y),
                (x, line_height / 2 + centre_offset_y),
            )

    def mainloop(self):
        window = pygame.display.set_mode((0, 0))

        pygame.mouse.set_visible(False)
        pygame.event.set_grab(True)

        self.running = True

        while self.running:
            self.update()
            self.draw(window)
            pygame.display.flip()


if __name__ == '__main__':
    game = RaycastingGame()

    game.mainloop()
