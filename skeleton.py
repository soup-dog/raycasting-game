from __future__ import annotations

from enemy import Enemy
from vector import Vector2
from sprite import Sprite
from animation import Animation
from utility import magnitude_2d
from typing import TYPE_CHECKING
import random

if TYPE_CHECKING:
    from game import RaycastingGame


class Skeleton(Enemy):
    WALK_NAME: str = "rot-skeleton-walk"
    WALK_COUNT: int = 8
    SLASH_NAME: str = "skeleton-slash"
    SLASH_COUNT: int = 4
    ATTACK_RANGE: float = 1
    SKELETON_TEXTURE: int = 0
    SLASH_TEXTURE: int = 1
    ATTACK_DAMAGE: float = 5
    MAX_HEALTH: float = 20

    def __init__(self, position: Vector2, game: RaycastingGame):
        super().__init__(position, Sprite(position, [None, None]), game, Skeleton.MAX_HEALTH)
        self.walk_animation = Animation.from_textures(self.game.data, Skeleton.WALK_NAME, Skeleton.WALK_COUNT)
        self.walk_animation.start()
        self.slash_animation = Animation.from_textures(self.game.data, Skeleton.SLASH_NAME, Skeleton.SLASH_COUNT)
        self.slash_animation.looping = False

    def attack(self):
        self.slash_animation.start()
        self.sprite.textures[Skeleton.SLASH_TEXTURE] = self.slash_animation.get_texture()
        self.sprite.textures[Skeleton.SLASH_TEXTURE].flip_x = random.getrandbits(1)
        self.game.player.take_hit(Skeleton.ATTACK_DAMAGE)

    def update(self, delta_time: float):
        super().update(delta_time)

        player_relative_position = self.game.player.position - self.position
        player_distance = magnitude_2d(player_relative_position)

        info = self.game.raycast(self.position, player_relative_position / player_distance, player_distance)

        if info.hit:  # can't see player
            if not self.pathfinding:
                self.follow_path_to(self.game.player.position)
        else:  # can see player
            self.go_to(self.game.player.position.copy())  # move directly to the player
            self.pathfinding = False

        self.sprite.textures[Skeleton.SKELETON_TEXTURE] = self.walk_animation.get_texture()
        self.sprite.textures[Skeleton.SKELETON_TEXTURE].flip_x = self.movement_relative_to_camera()[0] > 0  # flip texture if moving right relative to camera

        if self.slash_animation.running:
            self.sprite.textures[Skeleton.SLASH_TEXTURE] = self.slash_animation.get_texture()
        else:
            self.sprite.textures[Skeleton.SLASH_TEXTURE] = None
            if player_distance < Skeleton.ATTACK_RANGE:
                self.attack()
