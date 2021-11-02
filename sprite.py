from vector import Vector2
from data_manager import Texture


class Sprite:
    def __init__(self, position: Vector2, texture: Texture, texture_columns: list[Texture]):
        self.position: Vector2 = position
        self.texture: Texture = texture
        self.texture_columns: list[Texture] = texture_columns
