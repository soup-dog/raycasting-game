from __future__ import annotations

# standard
from abc import ABC, abstractmethod
from typing import TYPE_CHECKING
# project
from sprite import Sprite
from vector import Vector2

if TYPE_CHECKING:
    from game import RaycastingGame


class GameObject(ABC):
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

    def bind(self, game: RaycastingGame) -> GameObject:
        game.game_objects.append(self)
        game.sprites.append(self.sprite)
        return self

    def unbind(self, game: RaycastingGame):
        game.game_objects.remove(self)
        game.sprites.remove(self.sprite)

    @abstractmethod
    def update(self, delta_time: float):
        raise NotImplementedError()
