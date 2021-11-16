from __future__ import annotations

from enemy import Enemy
from vector import Vector2
from skeleton import Skeleton
# standard
from queue import Queue
import random
from typing import TYPE_CHECKING, Callable, Union
# pygame
import pygame
# numpy
import numpy as np

if TYPE_CHECKING:
    from game import RaycastingGame


WaveGenerator: Callable[[int], list[list[Enemy]]]


class EnemyManager:
    START_WAVE_SPAWN_DELAY: float = 1

    def __init__(self, game: RaycastingGame, spawn_locations: list[Vector2], waves: list[list[Enemy]], wave_generator: Union[WaveGenerator, None] = None):
        self.game = game
        self.spawn_locations: list[Vector2] = spawn_locations
        self.waves: list[list[Enemy]] = waves
        if wave_generator is None:
            wave_generator = self.generate_wave
        self.wave_generator: WaveGenerator = wave_generator
        self.wave: int = 0
        self.enemies: Queue[Enemy] = Queue()
        self.spawn_delay: float = 2
        self.last_spawn: int = 0

    def generate_wave(self, wave: int, enemies: Queue):
        for _ in range(wave):
            enemies.put(Skeleton(np.empty((2, ), dtype=float), self.game))

    def start(self):
        self.begin_wave(0)

    def begin_wave(self, wave: int):
        print("beginning wave", wave)
        if wave < len(self.waves):
            for enemy in self.waves[wave]:
                self.enemies.put(enemy)
        else:
            self.wave_generator(wave, self.enemies)

        self.last_spawn = pygame.time.get_ticks() - self.spawn_delay * 1000 + EnemyManager.START_WAVE_SPAWN_DELAY * 1000
        self.wave = wave

    def spawn_enemy(self):
        print("spawning enemy")
        spawn = random.choice(self.spawn_locations)
        enemy = self.enemies.get()
        enemy.position = spawn.copy()
        enemy.bind(self.game)
        self.last_spawn = pygame.time.get_ticks()

    def can_spawn_enemy(self):
        return not self.enemies.empty()

    def update(self, delta_time: float):
        time = pygame.time.get_ticks()

        if self.can_spawn_enemy():
            if (time - self.last_spawn) / 1000 > self.spawn_delay:
                self.spawn_enemy()
        else:
            self.begin_wave(self.wave + 1)
