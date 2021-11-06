from vector import Vector2
from data_manager import Texture


class Sprite:
    def __init__(self, position: Vector2, texture: Texture, texture_columns: list[Texture], scale: float = 1, height_offset: float = 0):
        self.position: Vector2 = position
        self.texture: Texture = texture
        self.texture_columns: list[Texture] = texture_columns
        self.scale: float = scale
        self.height_offset: float = height_offset
