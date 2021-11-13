from __future__ import annotations

import pygame.time
from texture import TextureData
from data_manager import DataManager


class Animation:
    def __init__(self, textures: list[TextureData], framerate: float = 10, looping: bool = True):
        self.textures: list[TextureData] = textures
        self.framerate: float = framerate
        self.looping: bool = looping
        self._started: bool = False
        self.start_time: int = -1

    @property
    def running(self):
        return self._started and (self.looping or (pygame.time.get_ticks() - self.start_time) / 1000 < len(self.textures) / self.framerate)

    def start(self):
        self.start_time = pygame.time.get_ticks()
        self._started = True

    def stop(self):
        self._started = False

    def get_texture(self) -> TextureData:
        if not self._started:
            raise Exception("Animation not started")

        time = (pygame.time.get_ticks() - self.start_time) / 1000
        frame = int((time * self.framerate)) + 1
        if self.looping:
            index = int(frame % len(self.textures))
        else:
            last_index = len(self.textures) - 1
            index = last_index if frame > last_index else frame
        return self.textures[index]

    @staticmethod
    def from_textures(data: DataManager, name: str, count: int, start: int = 1) -> Animation:
        return Animation([data.textures[name + str(i)] for i in range(start, count + 1)])
