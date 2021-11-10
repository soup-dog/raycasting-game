from __future__ import annotations

# standard
from abc import ABC, abstractmethod
from typing import TYPE_CHECKING
# project
from sprite import Sprite
from vector import Vector2
from data_manager import TextureData

if TYPE_CHECKING:
    from game import RaycastingGame


class Item(ABC):
    def __init__(self, position: Vector2, sprite: Sprite):
        self.sprite = sprite
        self.position = position

    @property
    def position(self) -> Vector2:
        return self._position

    @position.setter
    def position(self, value):
        self._position = value
        self.sprite.position = self._position

    def bind(self, game: RaycastingGame) -> Item:
        game.sprites.append(self.sprite)
        return self

    def unbind(self, game: RaycastingGame):
        game.sprites.remove(self.sprite)

    @abstractmethod
    def can_pickup(self) -> bool:
        raise NotImplementedError()

    @abstractmethod
    def pickup(self):
        raise NotImplementedError()

    def try_pickup(self):
        if self.can_pickup():
            self.pickup()
