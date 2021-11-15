from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from player import Player


class Weapon(ABC):
    def __init__(self, player: Player):
        self.player: Player = player

    @abstractmethod
    def attack(self):
        raise NotImplementedError()
