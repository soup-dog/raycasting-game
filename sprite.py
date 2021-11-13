from vector import Vector2
from texture import TextureData
from typing import Union


class Sprite:
    def __init__(self, position: Vector2, textures: list[Union[TextureData, None]] = None, scale: float = 1, height_offset: float = 0):
        self.position: Vector2 = position
        if textures is None:
            textures = []
        self.textures: list[Union[TextureData, None]] = textures
        self.scale: float = scale
        self.height_offset: float = height_offset

    @staticmethod
    def get_height_offset(scale: float) -> float:
        return 0.5 * scale - 0.5
