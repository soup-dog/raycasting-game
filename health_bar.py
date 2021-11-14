from data_manager import DataManager
from texture import Texture
from player import Player
import pygame
from pygame import Surface


class HealthBar:
    BASE_TEXTURE_NAME: str = "health-bar"
    STRIP_TEXTURE_NAME: str = "health-strip"
    BAR_LENGTH: int = 26
    STRIP_X_OFFSET: int = 3
    STRIP_Y_OFFSET: int = 6
    SCALE_RATIO: float = 0.2

    def __init__(self, data: DataManager):
        self.base_texture: Texture = data.textures[HealthBar.BASE_TEXTURE_NAME].texture
        self.strip_texture: Texture = data.textures[HealthBar.STRIP_TEXTURE_NAME].texture
        self.scaled_base: Texture = self.base_texture
        self.scaled_strips: Texture = self.strip_texture
        self.strip_width: int = 0
        self.strip_x_offset: int = 0
        self.strip_y_offset: int = 0

    def resize(self, size: tuple[int, int]):
        new_height = int(size[1] * HealthBar.SCALE_RATIO)  # new base texture height
        new_width = int(new_height * self.base_texture.get_width() / self.base_texture.get_height())  # new base texture width
        self.scaled_base = pygame.transform.scale(self.base_texture, (new_width, new_height))  # resize

        self.strip_width = new_height * self.strip_texture.get_width() / self.base_texture.get_height() # new width of single strip
        strips_height = int(self.strip_texture.get_height() / self.base_texture.get_height() * new_height)  # new height of strips
        strips_width = int(self.strip_width * HealthBar.BAR_LENGTH + 0.5)  # new width of all strips
        self.scaled_strips = pygame.transform.scale(self.strip_texture, (strips_width, strips_height))  # resize
        self.strip_x_offset = self.strip_width * HealthBar.STRIP_X_OFFSET + 1
        self.strip_y_offset = new_height / self.base_texture.get_height() * HealthBar.STRIP_Y_OFFSET + 1

    def draw(self, surface: Surface, position: tuple[int, int], player: Player):
        health_ratio = player.health / player.MAX_HEALTH
        surface.blit(
            self.scaled_strips,
            (position[0] + self.strip_x_offset, position[1] + self.strip_y_offset),
            pygame.Rect(0, 0, int(self.strip_width * health_ratio * HealthBar.BAR_LENGTH + 0.5), self.scaled_strips.get_height())
        )
        surface.blit(self.scaled_base, position)

