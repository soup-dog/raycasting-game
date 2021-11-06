import pygame
from data_manager import DataManager
from game import RaycastingGame
from argparse import ArgumentParser
import logging


pygame.init()


CONFIG_PATH = "config.ini"
TEXTURES_PATH = "textures"
MAPS_PATH = "maps"
LOG_PATH = "log.txt"

# from https://www.golinuxcloud.com/python-logging/
LOGGING_FORMAT = "[%(asctime)s] %(levelname)-8s %(name)-12s %(message)s"


if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument("--debug", action="store_true")

    args = parser.parse_args()

    data_manager = DataManager(
        config_path=CONFIG_PATH,
        textures_path=TEXTURES_PATH,
        maps_path=MAPS_PATH,
    )

    logging.basicConfig(format=LOGGING_FORMAT,
                        level=data_manager.config.getint("Logging", "level"),
                        filename=LOG_PATH)

    game = RaycastingGame(data_manager)

    if args.debug:
        logging.info("Launching in debug mode")
        from debug import RaycastingGameDebugger
        game_debugger = RaycastingGameDebugger(game)

        game_debugger.start()
        logging.debug("Debugger injection successful")

    logging.info("Entering mainloop")
    game.mainloop()

    logging.shutdown()
