# project
from game_map import MapHelper, Map
from texture import Texture, TextureData
# standard
import os
from configparser import ConfigParser
import logging
# pygame
import pygame
from pygame.mixer import Sound


DEFAULT_CONFIG = {
    "Input": {
        "mouse_sensitivity": 0.5
    },
    "Keymap": {
        "forward": pygame.K_w,
        "left": pygame.K_a,
        "back": pygame.K_s,
        "right": pygame.K_d,
        "run": pygame.K_LSHIFT,
    },
    "Behaviour": {
        "escape_behaviour": "quit"
    },
    "Logging": {
        "level": logging.WARNING
    },
    "Video": {
        "fullscreen": True,
        "scaled": True,
        "width": 750,
        "height": 500
    }
}


class DataManager:
    def __init__(self, textures_path: str, maps_path: str, sounds_path: str, config_path: str):
        self.textures: dict[str, TextureData] = DataManager.load_textures(textures_path)
        self.maps: dict[str, Map] = DataManager.load_maps(maps_path)
        self.sounds: dict[str, Sound] = DataManager.load_sounds(sounds_path)
        self.config: ConfigParser = DataManager.load_config(config_path)
        self.sounds_path: str = sounds_path
        self.config_path: str = config_path

    @staticmethod
    def load_textures(path: str) -> dict[str, TextureData]:
        return {os.path.splitext(file)[0]: TextureData.from_texture(pygame.image.load(os.path.join(path, file))) for file in os.listdir(path)}

    @staticmethod
    def load_maps(path: str) -> dict[str, Map]:
        return {os.path.splitext(file)[0]: MapHelper.load_map_file(os.path.join(path, file)) for file in os.listdir(path)}

    @staticmethod
    def load_sounds(path: str) -> dict[str, Sound]:
        return {os.path.splitext(file)[0]: Sound(os.path.join(path, file)) for file in os.listdir(path)}

    @staticmethod
    def load_config(path: str) -> ConfigParser:
        config = ConfigParser()
        config.read_dict(DEFAULT_CONFIG)
        config.read(path)

        return config

    def save_config(self):
        with open(self.config_path, "w") as f:
            self.config.write(f)


def get_sounds(data: DataManager, name: str, count: int, start: int = 1) -> list[Sound]:
    return [data.sounds[name + str(i)] for i in range(start, count + 1)]
