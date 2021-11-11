from __future__ import annotations

import numpy as np

from game_object import GameObject
from sprite import Sprite
from vector import Vector2
from utility import magnitude_2d
from data_manager import DataManager
from animation import Animation

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from game import RaycastingGame


class Rat(GameObject):
    TEXTURE_NAME = "regular-rat"
    TEXTURE_COUNT = 4
    SPRITE_SCALE = 0.3
    SPRITE_HEIGHT_OFFSET = Sprite.get_height_offset(SPRITE_SCALE)

    min_target_distance = 1
    speed = 1

    def __init__(self, position: Vector2, game: RaycastingGame):
        super().__init__(position, Rat.get_sprite(position, game.data))
        self.move_to_target: bool = False
        self.target_position: Vector2 = np.zeros((2, ))
        self.game: RaycastingGame = game
        self.animation = Animation.from_textures(self.game.data, Rat.TEXTURE_NAME, Rat.TEXTURE_COUNT)
        self.animation.start()

    @staticmethod
    def get_sprite(position: Vector2, data: DataManager) -> Sprite:
        return Sprite(position, data.textures[Rat.TEXTURE_NAME + str(Rat.TEXTURE_COUNT)], Rat.SPRITE_SCALE, Rat.SPRITE_HEIGHT_OFFSET)

    def get_target_position(self):
        return self.position + (np.random.random_sample((2, )) - 0.5) * 8

    def update(self, delta_time: float):
        if self.reached_target():
            self.target_position = self.get_target_position()

        relative_position = self.target_position - self.position
        direction = relative_position / magnitude_2d(relative_position)
        movement = direction * Rat.speed * delta_time

        self.position += movement

        self.sprite.texture = self.animation.get_texture()

        camera_movement = np.matmul(self.game.player.inv_camera_matrix, movement)
        self.sprite.texture.flip_x = camera_movement[0] > 0

    def reached_target(self) -> bool:
        return magnitude_2d(self.target_position - self.position) < Rat.min_target_distance
