import pygame
from configparser import ConfigParser
from game import RaycastingGame

pygame.init()


CONFIG_PATH = "config.ini"
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


if __name__ == '__main__':
    config = ConfigParser()
    config.read_dict(DEFAULT_CONFIG)
    config.read(CONFIG_PATH)

    game = RaycastingGame(config)

    game.mainloop()
