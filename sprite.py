from vector import Vector2
from texture import TextureData


class Sprite:
    def __init__(self, position: Vector2, textures: list[TextureData] = None, scale: float = 1, height_offset: float = 0):
        self.position: Vector2 = position
        if textures is None:
            textures = []
        self.textures: list[TextureData] = textures
        self.scale: float = scale
        self.height_offset: float = height_offset

    @staticmethod
    def get_height_offset(scale: float) -> float:
        return 0.5 * scale - 0.5
