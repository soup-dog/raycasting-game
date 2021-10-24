import pygame
from data_manager import DataManager
from game import RaycastingGame
from argparse import ArgumentParser

pygame.init()


CONFIG_PATH = "config.ini"
TEXTURES_PATH = "textures"
MAPS_PATH = "maps"


if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument("--debug", action="store_true")

    args = parser.parse_args()

    data_manager = DataManager(
        config_path=CONFIG_PATH,
        textures_path=TEXTURES_PATH,
        maps_path=MAPS_PATH,
    )

    game = RaycastingGame(data_manager)

    if args.debug:
        print("Launching in debug mode")
        from debug import RaycastingGameDebugger
        game_debugger = RaycastingGameDebugger()

        game_debugger.inject(game)

    game.mainloop()
