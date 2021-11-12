from __future__ import annotations

import numpy as np
import pygame.time

from game_object import GameObject
from sprite import Sprite
from vector import Vector2
from utility import magnitude_2d
from data_manager import DataManager
from animation import Animation
from agent import Agent, a_star, vector_to_point, random_goal

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from game import RaycastingGame


class Rat(Agent):
    WALK_NAME: str = "regular-rat"
    WALK_COUNT: int = 4
    IDLE_NAME: str = "regular-rat-idle"
    IDLE_COUNT: int = 2
    SPRITE_SCALE: float = 0.3
    SPRITE_HEIGHT_OFFSET: float = Sprite.get_height_offset(SPRITE_SCALE)
    SPEED: float = 1
    PATHFINDING_DELAY: float = 3000

    def __init__(self, position: Vector2, game: RaycastingGame):
        super().__init__(position, Rat.get_sprite(position, game.data), game, Rat.SPEED)
        self.game: RaycastingGame = game
        self.walk_animation = Animation.from_textures(self.game.data, Rat.WALK_NAME, Rat.WALK_COUNT)
        self.idle_animation = Animation.from_textures(self.game.data, Rat.IDLE_NAME, Rat.IDLE_COUNT)
        self.idle_animation.framerate = 2
        self.walk_animation.start()
        self.idle_animation.start()
        self.last_pathfinding_time: int = 0
        self.on_reached_goal.append(self.handle_reached_goal)
        self.set_random_goal()

    @staticmethod
    def get_sprite(position: Vector2, data: DataManager) -> Sprite:
        return Sprite(position, data.textures[Rat.IDLE_NAME + str(Rat.IDLE_COUNT)], Rat.SPRITE_SCALE, Rat.SPRITE_HEIGHT_OFFSET)

    def handle_reached_goal(self):
        self.last_pathfinding_time = pygame.time.get_ticks()

    def set_random_goal(self):
        self.follow_path(random_goal(vector_to_point(self.position), self.game.map))

    def update(self, delta_time: float):
        super().update(delta_time)

        if not self.pathfinding and pygame.time.get_ticks() - self.last_pathfinding_time > Rat.PATHFINDING_DELAY:
            self.set_random_goal()

        if self.pathfinding:
            self.sprite.texture = self.walk_animation.get_texture()
        else:
            self.sprite.texture = self.idle_animation.get_texture()

        camera_movement = np.matmul(self.game.player.inv_camera_matrix, self.movement)
        self.sprite.texture.flip_x = camera_movement[0] > 0
