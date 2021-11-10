from __future__ import annotations

from pygame import Surface, PixelArray


Texture = Surface


class TextureData:
    def __init__(self, texture: Texture, columns: list[Texture]):
        self.texture: Texture = texture
        self.columns: list[Texture] = columns

    @staticmethod
    def texture_to_columns(texture: Texture) -> list[Texture]:
        pixel_array = PixelArray(texture).transpose()
        return [pixel_array[:, col].transpose().make_surface() for col in range(pixel_array.shape[0])]

    @staticmethod
    def from_texture(texture: Texture) -> TextureData:
        return TextureData(texture, TextureData.texture_to_columns(texture))