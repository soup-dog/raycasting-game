from __future__ import annotations

from vector import Vector2
from sprite import Sprite
from item import Item
from player import Player
from utility import magnitude_2d
from typing import TYPE_CHECKING
import math

if TYPE_CHECKING:
    from game import RaycastingGame


class Coin(Item):
    TEXTURE_NAME = "coin"
    SPRITE_SCALE = 0.1
    SPRITE_HEIGHT_OFFSET = Sprite.get_height_offset(SPRITE_SCALE)
    COIN_FLOAT_DISTANCE = 0.5

    pickup_distance = 1

    def __init__(self, position: Vector2, game: RaycastingGame, player: Player, value: int = 1):
        super().__init__(position, Sprite(position, game.data.textures[Coin.TEXTURE_NAME], Coin.SPRITE_SCALE, Coin.SPRITE_HEIGHT_OFFSET))
        self.player: Player = player
        self.value: int = value
        self.game: RaycastingGame = game

    def update(self, delta_time: float):
        self.try_pickup()

    def bind(self, game: RaycastingGame) -> Item:
        old = super().bind(game)
        game.on_update.append(self.update)
        return old

    def unbind(self, game: RaycastingGame):
        old = super().unbind(game)
        game.on_update.remove(self.update)
        return old

    def can_pickup(self) -> bool:
        return magnitude_2d(self.position - self.player.position) < Coin.pickup_distance

    def pickup(self):
        self.player.money += self.value
        self.unbind(self.game)
