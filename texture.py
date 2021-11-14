from __future__ import annotations

from pygame import Surface, PixelArray


Texture = Surface
empty_surface = Surface((0, 0))


class TextureData:
    def __init__(self, texture: Texture, columns: list[Texture], flip_x: bool = False, simple_clip: bool = False):
        self.texture: Texture = texture
        self.columns: list[Texture] = columns
        self.flip_x: bool = flip_x
        self.simple_clip: bool = simple_clip

    @staticmethod
    def texture_to_columns(texture: Texture) -> list[Texture]:
        pixel_array = PixelArray(texture).transpose()
        return [pixel_array[:, col].transpose().make_surface() for col in range(pixel_array.shape[1])]

    @staticmethod
    def from_texture(texture: Texture) -> TextureData:
        return TextureData(texture, TextureData.texture_to_columns(texture))
