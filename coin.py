from __future__ import annotations

from vector import Vector2
from sprite import Sprite
from item import Item
from player import Player
from utility import magnitude_2d
from typing import TYPE_CHECKING
from data_manager import DataManager
import math
import pygame.time

if TYPE_CHECKING:
    from game import RaycastingGame


class Coin(Item):
    TEXTURE_NAME = "coin"
    SPRITE_SCALE = 0.25
    SPRITE_HEIGHT_OFFSET = Sprite.get_height_offset(SPRITE_SCALE)
    COIN_FLOAT_DISTANCE = 0.1

    pickup_distance = 1

    def __init__(self, position: Vector2, game: RaycastingGame, player: Player, value: int = 1):
        super().__init__(position, Coin.get_sprite(position, game.data))
        self.player: Player = player
        self.value: int = value
        self.game: RaycastingGame = game

    @staticmethod
    def get_sprite(position: Vector2, data: DataManager) -> Sprite:
        return Sprite(position, data.textures[Coin.TEXTURE_NAME], Coin.SPRITE_SCALE, Coin.SPRITE_HEIGHT_OFFSET)

    def update(self, delta_time: float):
        self.try_pickup()
        self.sprite.height_offset = Coin.SPRITE_HEIGHT_OFFSET + (math.sin(pygame.time.get_ticks() / 1000) + 1) * Coin.COIN_FLOAT_DISTANCE

    def can_pickup(self) -> bool:
        return magnitude_2d(self.position - self.player.position) < Coin.pickup_distance

    def pickup(self):
        self.player.money += self.value
        self.unbind(self.game)
