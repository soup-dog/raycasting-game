from vector import Vector2
from texture import TextureData


class Sprite:
    def __init__(self, position: Vector2, texture: TextureData, scale: float = 1, height_offset: float = 0):
        self.position: Vector2 = position
        self.texture: TextureData = texture
        self.scale: float = scale
        self.height_offset: float = height_offset

    @staticmethod
    def get_height_offset(scale: float) -> float:
        return 0.5 * scale - 0.5
