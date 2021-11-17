from __future__ import annotations

from texture import Texture
from animation import Animation
from utility import scale_by_height
from colour import ColourType
import pygame
from pygame import Surface, Rect
from typing import TYPE_CHECKING, Callable

if TYPE_CHECKING:
    from game import RaycastingGame


class Button:
    def __init__(self, texture: Texture, position: tuple[int, int] = (0, 0), relative_scale: float = 0.2):
        self._texture: Texture = texture
        self.scaled_texture: Texture = texture
        self.texture: Texture = texture
        self.position: tuple[int, int] = position
        self.rect: Rect = self.get_rect()
        self.relative_scale: float = relative_scale
        self.selected: bool = False

    def resize(self, size: tuple[int, int]):
        self.scaled_texture = scale_by_height(self._texture, int(size[1] * self.relative_scale))
        self.update_texture()

    def update_rect(self):
        self.rect = self.get_rect()

    def update_texture(self):
        self.texture = self.scaled_texture.copy()
        if not self.selected:
            self.texture.fill((150, 150, 150, 255), None, special_flags=pygame.BLEND_RGBA_MULT)

    def draw_centred(self, surface: Surface):
        surface.blit(self.texture, self.rect)

    def get_rect(self):
        return Rect(self.position[0], self.position[1], self.texture.get_width(), self.texture.get_height())

    def update_selected(self, mouse_pos: tuple[int, int]):
        old = self.selected
        self.selected = self.rect.collidepoint(mouse_pos[0], mouse_pos[1])

        if self.selected != old:
            self.update_texture()


class UIRenderer:
    TITLE: str = "title"
    TITLE_COUNT: int = 8
    START_BUTTON: str = "start-button"
    QUIT_BUTTON: str = "quit-button"
    AGAIN_BUTTON: str = "again-button"
    TITLE_SCALE: float = 0.3
    BUTTON_SCALE: float = 0.2
    BUTTON_MARGIN: float = 0.1
    TITLE_BACKGROUND_COLOUR: ColourType = (10, 0, 10)

    def __init__(self, game: RaycastingGame):
        self.game: RaycastingGame = game
        self.title_animation: Animation = Animation.from_textures(game.data, UIRenderer.TITLE, UIRenderer.TITLE_COUNT)
        self.title_animation.framerate = 5
        self.title_animation.start()
        self.start_button: Button = Button(game.data.textures[UIRenderer.START_BUTTON].texture)
        self.quit_button: Button = Button(game.data.textures[UIRenderer.QUIT_BUTTON].texture)
        self.again_button: Button = Button(game.data.textures[UIRenderer.AGAIN_BUTTON].texture)
        self.buttons: list[Button] = [
            self.start_button,
            self.quit_button,
            self.again_button
        ]
        self.title_button_map: list[tuple[Button, Callable]] = [
            (self.start_button, game.start_game),
            (self.quit_button, game.quit),
        ]
        self.gameover_button_map: list[tuple[Button, Callable]] = [
            (self.again_button, game.start_game),
            (self.quit_button, game.quit),
        ]

    def resize(self, size: tuple[int, int]):
        for button in self.buttons:
            button.resize(size)

        screen_centre_x = size[0] / 2
        button_start_y = size[1] * 0.5
        button_offset_y = self.start_button.texture.get_height() * (UIRenderer.BUTTON_MARGIN + 1)

        self.start_button.position = (screen_centre_x - self.start_button.texture.get_width() / 2, button_start_y)
        self.again_button.position = self.start_button.position
        self.quit_button.position = (screen_centre_x - self.quit_button.texture.get_width() / 2, button_start_y + button_offset_y)

        for button in self.buttons:
            button.update_rect()

    def update_mouse(self, mouse_pos: tuple[int, int]):
        for button in self.buttons:
            button.update_selected(mouse_pos)

    def handle_click(self):
        if self.game.draw_mode == self.game.DrawMode.TITLE:
            for button, f in self.title_button_map:
                if button.selected:
                    f()
        elif self.game.draw_mode == self.game.DrawMode.GAMEOVER:
            for button, f in self.gameover_button_map:
                if button.selected:
                    f()

    def draw_title(self, surface: Surface):
        surface.fill(UIRenderer.TITLE_BACKGROUND_COLOUR)

        screen_centre_x = surface.get_width() / 2

        scaled_title = scale_by_height(self.title_animation.get_texture().texture, int(surface.get_height() * UIRenderer.TITLE_SCALE))
        surface.blit(scaled_title, (screen_centre_x - scaled_title.get_width() / 2, surface.get_height() / 4 - scaled_title.get_height() / 2))

        self.start_button.draw_centred(surface)
        self.quit_button.draw_centred(surface)

    def draw_gameover(self, surface: Surface):
        self.again_button.draw_centred(surface)
        self.quit_button.draw_centred(surface)
