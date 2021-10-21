import pygame
from data_manager import DataManager
from game import RaycastingGame

pygame.init()


CONFIG_PATH = "config.ini"
TEXTURES_PATH = "textures"
MAPS_PATH = "maps"


if __name__ == '__main__':
    data_manager = DataManager(
        config_path=CONFIG_PATH,
        textures_path=TEXTURES_PATH,
        maps_path=MAPS_PATH,
    )

    game = RaycastingGame(data_manager)

    game.mainloop()
