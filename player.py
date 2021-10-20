import numpy as np
from numpy.typing import NDArray
import pygame
from pygame.event import Event
from utility import angle_between_vectors, rotation_matrix
from configparser import ConfigParser


class PlayerSettings:
    def __init__(self):
        self.turn_speed: float = 0
        self.walk_speed: float = 0
        self.run_speed: float = 0

    @staticmethod
    def get_default_settings():
        settings = PlayerSettings()
        settings.turn_speed = 1
        settings.walk_speed = 1
        settings.run_speed = 1
        return settings


class Player:
    def __init__(self, config: ConfigParser, position: NDArray[float] = None, direction: NDArray[float] = None, camera_plane: NDArray[float] = None):
        self.config = config
        if position is None:
            position = np.zeros((2, ), dtype=float)
        if direction is None:
            direction = np.array([1, 0], dtype=float)
        if camera_plane is None:
            camera_plane = np.array([0, 0.66], dtype=float)
        self.settings: PlayerSettings = PlayerSettings.get_default_settings()
        self.velocity: NDArray[float] = np.zeros((2, ), dtype=float)
        self.position: NDArray[float] = position
        self.camera_plane: NDArray[float] = camera_plane
        self.camera_plane_matrix: NDArray[float] = rotation_matrix(-angle_between_vectors(direction, self.camera_plane))
        self.forward: NDArray[float] = direction
        self.right: NDArray[float] = np.array([direction[1], direction[0]], dtype=float)
        self.running = False

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

        norm = np.linalg.norm(movement)

        if norm == 0:  # avoid divide by infinity
            return movement  # (0, 0)

        return movement / np.linalg.norm(movement)  # normalise vector

    @property
    def current_speed(self):
        return self.settings.run_speed if self.running else self.settings.walk_speed

    def update(self, delta_time: float):
        keymap = self.config["Keymap"]
        pressed = pygame.key.get_pressed()

        movement = self.get_movement_vector(
            pressed[keymap.getint("forward")],
            pressed[keymap.getint("back")],
            pressed[keymap.getint("left")],
            pressed[keymap.getint("right")],
        )

        self.position += movement * self.current_speed * delta_time

    def rotate(self, rotation_matrix: NDArray[float]):
        self.set_direction(np.dot(self.forward, rotation_matrix))
        # self.forward = np.dot(self.forward, rotation_matrix)
        # self.camera_plane = np.dot(self.camera_plane, rotation_matrix)
        # self.camera_plane = np.dot(self.forward, self.camera_plane_matrix)

    def set_direction(self, direction: NDArray[float]):
        self.forward = direction
        self.right = np.array([-direction[1], direction[0]], dtype=float)
        self.camera_plane = np.dot(self.forward, self.camera_plane_matrix)
