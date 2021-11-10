from __future__ import annotations

import numpy as np

from game_object import GameObject
from sprite import Sprite
from vector import Vector2
from utility import magnitude_2d
from coin import Coin
from data_manager import DataManager

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from game import RaycastingGame


class Rat(GameObject):
    SPRITE_SCALE = 0.3
    SPRITE_HEIGHT_OFFSET = Sprite.get_height_offset(SPRITE_SCALE)

    min_target_distance = 1
    speed = 1

    def __init__(self, position: Vector2, game: RaycastingGame):
        super().__init__(position, Rat.get_sprite(position, game.data))
        self.move_to_target: bool = False
        self.target_position: Vector2 = np.zeros((2, ))
        self.game: RaycastingGame = game

    @staticmethod
    def get_sprite(position: Vector2, data: DataManager) -> Sprite:
        return Sprite(position, data.textures["regular-rat1"], Rat.SPRITE_SCALE, Rat.SPRITE_HEIGHT_OFFSET)

    def update(self, delta_time: float):
        if self.reached_target():
            self.target_position = np.random.random_sample((2, )) * self.game.map.shape

        relative_position = self.target_position - self.position
        direction = relative_position / magnitude_2d(relative_position)
        movement = direction * Rat.speed * delta_time

        self.position += movement

    def reached_target(self) -> bool:
        return magnitude_2d(self.target_position - self.position) < Rat.min_target_distance

    def bind(self, game: RaycastingGame) -> GameObject:
        base = super().bind(game)
        game.on_update.append(self.update)
        return base

    def unbind(self, game: RaycastingGame):
        super().unbind(game)
        game.on_update.remove(self.update)