# project
from game_map import MapHelper, Map
# standard
import os
from configparser import ConfigParser
# pygame
import pygame


DEFAULT_CONFIG = {
    "Input": {
        "mouse_sensitivity": 1
    },
    "Keymap": {
        "forward": pygame.K_w,
        "left": pygame.K_a,
        "back": pygame.K_s,
        "right": pygame.K_d,
        "run": pygame.K_LSHIFT,
    }
}


Texture = pygame.PixelArray


class DataManager:
    def __init__(self, textures_path: str, maps_path: str, config_path: str):
        self.textures: dict[str, Texture] = DataManager.load_textures(textures_path)
        self.maps: dict[str, Map] = DataManager.load_maps(maps_path)
        self.config: ConfigParser = DataManager.load_config(config_path)

    @staticmethod
    def load_textures(path: str) -> dict[str, Texture]:
        return {os.path.splitext(file)[0]: pygame.PixelArray(pygame.image.load(os.path.join(path, file))) for file in os.listdir(path)}

    @staticmethod
    def load_maps(path: str) -> dict[str, Map]:
        return {os.path.splitext(file)[0]: MapHelper.load_map_file(os.path.join(path, file)) for file in os.listdir(path)}

    @staticmethod
    def load_config(path: str) -> ConfigParser:
        config = ConfigParser()
        config.read_dict(DEFAULT_CONFIG)
        config.read(path)

        return config