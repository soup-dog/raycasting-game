from __future__ import annotations

from agent import Agent
from vector import Vector2
from sprite import Sprite
from typing import TYPE_CHECKING
from game_object import GameObject

if TYPE_CHECKING:
    from game import RaycastingGame


class Enemy(Agent):
    def __init__(self, position: Vector2, sprite: Sprite, game: RaycastingGame, max_health: float):
        super().__init__(position, sprite, game)
        self.max_health = max_health
        self.health = max_health

    def take_hit(self, damage: float):
        self.health -= damage
        if self.health <= 0:
            self.die()

    def die(self):
        self.unbind(self.game)

    def bind(self, game: RaycastingGame) -> GameObject:
        base = super().bind(game)
        game.enemies.append(self)
        return base

    def unbind(self, game: RaycastingGame):
        super().unbind(game)
        game.enemies.remove(self)
