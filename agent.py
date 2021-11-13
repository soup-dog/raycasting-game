from __future__ import annotations

# project
from game_object import GameObject
from vector import Vector2
from sprite import Sprite
from game_map import Map
from utility import magnitude_2d
# numpy
import numpy as np
# standard
from queue import Queue
from typing import TYPE_CHECKING, Iterator, Callable
import random

if TYPE_CHECKING:
    from game import RaycastingGame


Point = tuple[int, int]


def get_neighbours(position: Point, game_map: Map):
    neighbours = []
    # +x
    if position[0] != game_map.shape[0] - 1 and game_map[position[0] + 1, position[1]] == 0:
        neighbours.append((position[0] + 1, position[1]))
    # -x
    if position[0] != 0 and game_map[position[0] - 1, position[1]] == 0:
        neighbours.append((position[0] - 1, position[1]))
    # +y
    if position[1] != game_map.shape[1] - 1 and game_map[position[0], position[1] + 1] == 0:
        neighbours.append((position[0], position[1] + 1))
    # -y
    if position[1] != 0 and game_map[position[0], position[1] - 1] == 0:
        neighbours.append((position[0], position[1] - 1))

    return neighbours


def a_star(start: Point, goal: Point, game_map: Map) -> tuple[bool, list[Point]]:
    border = Queue()
    border.put(start)
    came_from = {start: None}

    while not border.empty():
        current = border.get()

        if current == goal:  # possible path found
            break

        # for each neighbour of the current cell
        for neighbour in get_neighbours(current, game_map):
            if neighbour not in came_from:  # if we haven't already reached the cell
                border.put(neighbour)  # add cell to the border
                came_from[neighbour] = current  # add an entry so that we can retrace later

        if border.empty():  # the goal position is inaccessible
            return False, []

    current = goal
    path = []
    # retrace steps in reverse
    while current != start:
        path.append(current)
        current = came_from[current]
    path.append(start)  # add start position
    path.reverse()  # reverse path

    return True, path


def random_goal(start: Point, game_map: Map) -> list[Point]:
    border = Queue()
    border.put(start)
    came_from = {start: None}

    while not border.empty():
        current = border.get()

        for neighbour in get_neighbours(current, game_map):
            if neighbour not in came_from:
                border.put(neighbour)
                came_from[neighbour] = current

    current = random.choice(list(came_from.keys()))
    path = []
    # retrace steps in reverse
    while current != start:
        path.append(current)
        current = came_from[current]
    path.append(start)  # add start position
    path.reverse()  # reverse path

    return path


def vector_to_point(vector: Vector2) -> Point:
    return int(vector[1]), int(vector[0])


def point_to_centre_vector(point: Point) -> Vector2:
    return np.array([point[1] + 0.5, point[0] + 0.5], dtype=float)


class Agent(GameObject):
    min_goal_distance: float = 0.3

    def __init__(self, position: Vector2, sprite: Sprite, game: RaycastingGame, speed: float = 1):
        super().__init__(position, sprite)
        self.pathfinding: bool = False
        self.moving: bool = False
        self.goal: Vector2 = np.zeros((2, ))
        self.path: Iterator[Point] = iter([])
        self.game: RaycastingGame = game
        self.speed: float = speed
        self.movement: Vector2 = np.zeros((2, ))
        self.on_reached_goal: list[Callable] = []

    def follow_path_to(self, goal: Vector2) -> bool:
        accessible, path = iter(a_star(vector_to_point(self.position), vector_to_point(goal), self.game.map))
        self.follow_path(path)
        return accessible

    def follow_path(self, path: list[Point]):
        self.pathfinding = True
        self.moving = True
        self.path = iter(path)
        self.next_goal()

    def end_path(self):
        self.pathfinding = False  # stop pathfinding
        self.moving = False
        for f in self.on_reached_goal:  # invoke each on_reached_goal callback
            f()

    def next_goal(self) -> bool:
        try:
            self.goal = point_to_centre_vector(next(self.path))
            return True
        except StopIteration:
            return False

    def go_to(self, goal: Vector2):
        self.goal = goal
        self.moving = True

    def reached_goal(self) -> bool:
        return magnitude_2d(self.goal - self.position) < Agent.min_goal_distance

    def random_point(self) -> Point:
        return random.randint(0, self.game.map.shape[0]), random.randint(0, self.game.map.shape[1])

    def flip_texture_relative_to_camera(self):
        # calculate movement relative to player camera
        camera_movement = np.matmul(self.game.player.inv_camera_matrix, self.movement)
        self.sprite.texture.flip_x = camera_movement[0] > 0  # flip if moving right relative to camera

    def update(self, delta_time: float):
        if self.reached_goal():
            # if pathfinding move to next goal if there is one
            if self.pathfinding and not self.next_goal():
                # if there is no next goal then
                self.end_path()

        if self.moving:
            relative_position = self.goal - self.position  # find position relative to goal
            direction = relative_position / magnitude_2d(relative_position)  # calculate direction by normalising relative position
            movement = direction * self.speed * delta_time  # determine movement based on speed and delta time

            self.movement = movement  # set movement
            self.position += movement  # move
