from __future__ import annotations

# numpy
import numpy as np
from numpy_typing import NDArray
# pygame
import pygame
# project
from utility import magnitude_2d
from vector import Vector2
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
    COLLISION_DISTANCE_OFFSET: float = -0.1
    MAX_HEALTH: float = 100

    def __init__(self, config: ConfigParser, game: RaycastingGame, position: Vector2 = None, direction: Vector2 = None, camera_plane_length: float = 1.5):
        self.config: ConfigParser = config
        self.game: RaycastingGame = game
        if position is None:
            position = np.zeros((2, ), dtype=float)
        if direction is None:
            direction = np.array([0, 1], dtype=float)
        self.settings: PlayerSettings = PlayerSettings()
        self.velocity: Vector2 = np.zeros((2, ), dtype=float)
        self.position: Vector2 = position
        self.forward: Vector2 = direction
        self.right: Vector2 = np.array([-direction[1], direction[0]], dtype=float)
        self.camera_plane_length = camera_plane_length
        self.camera_plane: Vector2 = camera_plane_length * self.right
        self.inv_camera_matrix: NDArray[float] = np.linalg.inv(np.array([
            [self.camera_plane[0], direction[0]],
            [self.camera_plane[1], direction[1]]
        ], dtype=float))
        self.clip: bool = True
        self.money: int = 0
        self.health: float = Player.MAX_HEALTH

    def take_hit(self, damage: float):
        self.health -= damage
        if self.health <= 0:
            self.game.game_over()

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

        if norm == 0:  # avoid divide by zero
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

        if self.clip:
            velocity_magnitude = magnitude_2d(velocity)

            info = self.game.raycast(self.position, velocity)

            distance = magnitude_2d(self.position - info.collision) + Player.COLLISION_DISTANCE_OFFSET

            # object was hit closer than current destination (i.e. there's a wall in the way)
            if info.hit and distance < velocity_magnitude:
                velocity = distance * (velocity / velocity_magnitude)

        self.position += velocity

    def rotate(self, rotation_matrix: Vector2):
        self.set_direction(np.matmul(rotation_matrix, self.forward))
        # self.forward = np.dot(self.forward, rotation_matrix)
        # self.camera_plane = np.dot(self.camera_plane, rotation_matrix)
        # self.camera_plane = np.dot(self.forward, self.camera_plane_matrix)

    def set_direction(self, direction: Vector2):
        self.forward = direction
        self.right = np.array([-direction[1], direction[0]], dtype=float)
        self.camera_plane = self.camera_plane_length * self.right
        self.inv_camera_matrix = np.linalg.inv(np.array([
            [self.camera_plane[0], self.forward[0]],
            [self.camera_plane[1], self.forward[1]]
        ], dtype=float))
