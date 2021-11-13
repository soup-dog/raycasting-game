from __future__ import annotations

# pygame
import pygame.time
# project
from sprite import Sprite
from vector import Vector2
from animation import Animation
from agent import Agent, vector_to_point, random_goal
# standard
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
        super().__init__(
            position,
            Sprite(position, [None], scale=Rat.SPRITE_SCALE, height_offset=Rat.SPRITE_HEIGHT_OFFSET),
            game,
            Rat.SPEED
        )
        self.game: RaycastingGame = game
        self.walk_animation: Animation = Animation.from_textures(self.game.data, Rat.WALK_NAME, Rat.WALK_COUNT)
        self.idle_animation: Animation = Animation.from_textures(self.game.data, Rat.IDLE_NAME, Rat.IDLE_COUNT)
        self.idle_animation.framerate = 2
        self.walk_animation.start()
        self.idle_animation.start()
        self.last_pathfinding_time: int = 0
        self.on_reached_goal.append(self.handle_reached_goal)
        self.set_random_goal()

    def handle_reached_goal(self):
        self.last_pathfinding_time = pygame.time.get_ticks()

    def set_random_goal(self):
        self.follow_path(random_goal(vector_to_point(self.position), self.game.map))

    def update(self, delta_time: float):
        super().update(delta_time)

        if not self.pathfinding and pygame.time.get_ticks() - self.last_pathfinding_time > Rat.PATHFINDING_DELAY:
            self.set_random_goal()

        if self.moving:  # if going somewhere
            self.sprite.textures[0] = self.walk_animation.get_texture()  # use a texture from the walking animation
        else:
            self.sprite.textures[0] = self.idle_animation.get_texture()  # otherwise use a texture from idle animation

        self.sprite.textures[0].flip_x = self.movement_relative_to_camera()[0] > 0  # flip texture if moving right relative to camera
