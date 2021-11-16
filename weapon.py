from __future__ import annotations

from texture import TextureData
from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from player import Player


class Weapon(ABC):
    def __init__(self, player: Player):
        self.player: Player = player

    @abstractmethod
    def get_window_scale(self) -> float:
        raise NotImplementedError()

    @abstractmethod
    def get_texture(self) -> TextureData:
        raise NotImplementedError()

    @abstractmethod
    def attack(self):
        raise NotImplementedError()
