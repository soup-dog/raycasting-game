from __future__ import annotations

import pygame.time
from texture import TextureData
from data_manager import DataManager


class Animation:
    def __init__(self, textures: list[TextureData], framerate: float = 10, loop: bool = True):
        self.textures: list[TextureData] = textures
        self.framerate: float = framerate
        self.looping: bool = loop
        self.start_time: int = -1

    def start(self):
        self.start_time = pygame.time.get_ticks()

    def get_texture(self) -> TextureData:
        time = (pygame.time.get_ticks() - self.start_time) / 1000
        frame = (time * self.framerate) + 1
        if self.looping:
            index = int(frame % len(self.textures))
        else:
            last_index = len(self.textures) - 1
            index = last_index if frame > last_index else frame
        return self.textures[index]

    @staticmethod
    def from_textures(data: DataManager, name: str, stop: int, start: int = 1) -> Animation:
        return Animation([data.textures[name + str(i)] for i in range(start, stop)])
