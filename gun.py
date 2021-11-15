from __future__ import annotations

from weapon import Weapon
from utility import magnitude_2d
from typing import TYPE_CHECKING
import numpy as np

if TYPE_CHECKING:
    from player import Player


class Pistol(Weapon):
    DAMAGE: float = 5

    def __init__(self, player: Player):
        super().__init__(player)

    def attack(self):
        for target in self.player.game.enemies:
            # calculate enemy camera position
            camera_position = np.matmul(self.player.inv_camera_matrix, target.position - self.player.position)
            # calculate portion of the screen that the enemy takes up
            width = abs(target.sprite.scale / camera_position[1] * target.sprite.textures[0].texture.get_width() / target.sprite.textures[0].texture.get_height())

            if abs(camera_position[0]) < width / 2:  # if crosshair is on enemy
                enemy_distance = magnitude_2d(target.position - self.player.position)

                info = self.player.game.raycast(self.player.position, self.player.forward, enemy_distance)

                if not info.hit:  # no walls in the way
                    target.take_hit(Pistol.DAMAGE)
