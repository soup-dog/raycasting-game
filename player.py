from __future__ import annotations

# numpy
import numpy as np
from numpy.typing import NDArray
# pygame
import pygame
# project
from utility import angle_between_vectors, rotation_matrix, magnitude_2d
# standard
from configparser import ConfigParser
from typing import TYPE_CHECKING

# typing
if TYPE_CHECKING:
    from game import RaycastingGame


class PlayerSettings:
    def __init__(self):
        self.turn_speed: float = 1
        self.walk_speed: float = 1
        self.run_speed: float = 5


class Player:
    COLLISION_DISTANCE_OFFSET: float = -0.0001

    def __init__(self, config: ConfigParser, game: RaycastingGame, position: NDArray[float] = None, direction: NDArray[float] = None, camera_plane: NDArray[float] = None):
        self.config: ConfigParser = config
        self.game: RaycastingGame = game
        if position is None:
            position = np.zeros((2, ), dtype=float)
        if direction is None:
            direction = np.array([1, 0], dtype=float)
        if camera_plane is None:
            camera_plane = np.array([0, 0.66], dtype=float)
        self.settings: PlayerSettings = PlayerSettings()
        self.velocity: NDArray[float] = np.zeros((2, ), dtype=float)
        self.position: NDArray[float] = position
        self.camera_plane: NDArray[float] = camera_plane
        self.camera_plane_matrix: NDArray[float] = rotation_matrix(-angle_between_vectors(direction, self.camera_plane))
        self.forward: NDArray[float] = direction
        self.right: NDArray[float] = np.array([direction[1], direction[0]], dtype=float)

    def get_movement_vector(self, forward, back, left, right):
        movement = np.zeros((2, ), dtype=float)

        if forward:
            movement += self.forward
        if back:
            movement -= self.forward
        if left:
            movement -= self.right
        if right:
            movement += self.right

        norm = magnitude_2d(movement)

        if norm == 0:  # avoid divide by infinity
            return movement  # (0, 0)

        return movement / norm  # normalise vector

    def get_current_speed(self, running: bool):
        return self.settings.run_speed if running else self.settings.walk_speed

    def update(self, delta_time: float):
        keymap = self.config["Keymap"]
        pressed = pygame.key.get_pressed()

        movement = self.get_movement_vector(
            pressed[keymap.getint("forward")],
            pressed[keymap.getint("back")],
            pressed[keymap.getint("left")],
            pressed[keymap.getint("right")],
        )

        velocity = movement * self.get_current_speed(pressed[keymap.getint("run")]) * delta_time
        velocity_magnitude = magnitude_2d(velocity)

        hit, _, collision = self.game.raycast(self.position, velocity)

        distance = magnitude_2d(self.position - collision) + Player.COLLISION_DISTANCE_OFFSET

        # object was hit closer than current destination (i.e. there's a wall in the way)
        if hit and distance < velocity_magnitude:
            velocity = distance * (velocity / velocity_magnitude)

        self.position += velocity

    def rotate(self, rotation_matrix: NDArray[float]):
        self.set_direction(np.dot(self.forward, rotation_matrix))
        # self.forward = np.dot(self.forward, rotation_matrix)
        # self.camera_plane = np.dot(self.camera_plane, rotation_matrix)
        # self.camera_plane = np.dot(self.forward, self.camera_plane_matrix)

    def set_direction(self, direction: NDArray[float]):
        self.forward = direction
        self.right = np.array([-direction[1], direction[0]], dtype=float)
        self.camera_plane = np.dot(self.forward, self.camera_plane_matrix)
