from game import RaycastingGame
import logging
from typing import Callable
import pygame
from pygame.freetype import SysFont


pygame.init()


PayloadMethod = Callable[[Callable, ...], None]

debugger_logger = logging.getLogger("debugger")


class Payload:
    def __init__(self, before: PayloadMethod = None, after: PayloadMethod = None):
        self._before: PayloadMethod = before
        self._after: PayloadMethod = after

    def before(self, *args, **kwargs):
        if self._before is not None:
            self._before(*args, **kwargs)

    def after(self, *args, **kwargs):
        if self._after is not None:
            self._after(*args, **kwargs)


class Debugger:
    @staticmethod
    def standard_inject(payload: Payload, instance: object, target_name: str) -> Callable:
        debugger_logger.debug(f"Standard injecting payload {payload} into method {target_name} of instance {instance}")
        target = getattr(instance, target_name)

        def injection(*args, **kwargs):
            payload.before(target, *args, **kwargs)
            result = target(*args, **kwargs)
            payload.after(target, *args, **kwargs)
            return result
        setattr(instance, target_name, injection)

        return injection


class RaycastingGameDebugger(Debugger):
    DEBUG_MOD_KEY = pygame.KMOD_LSHIFT

    def __init__(self, instance: RaycastingGame):
        self.delta_time = 0
        self.font: SysFont = SysFont("", 30)
        self.instance: RaycastingGame = instance
        self.show_debug_info: bool = True

    def toggle_noclip(self, event):
        if event.mod == RaycastingGameDebugger.DEBUG_MOD_KEY and event.type == pygame.KEYDOWN:
            self.instance.player.clip = not self.instance.player.clip

    def toggle_debug_info(self, event):
        if event.mod == RaycastingGameDebugger.DEBUG_MOD_KEY and event.type == pygame.KEYDOWN:
            self.show_debug_info = not self.show_debug_info

    def update_payload_before(self, target: Callable, *args, **kwargs):
        self.delta_time = args[0]

    def draw_payload_after(self, target: Callable, *args, **kwargs):
        if not self.show_debug_info:
            return

        surface = args[0]

        lines = [
            str(1 / self.delta_time),
            str(target.__self__.game.player.camera_plane),
            str(target.__self__.game.player.forward),
            str(target.__self__.game.player.position),
            "NOCLIP" if not self.instance.player.clip else ""
        ]

        for i in range(len(lines)):
            self.font.render_to(surface, (0, self.font.size * i), lines[i])

    def inject(self, instance: RaycastingGame):
        RaycastingGameDebugger.standard_inject(Payload(self.update_payload_before), instance, "update")
        instance.draw_mode_map[RaycastingGame.DrawMode.GAME] = RaycastingGameDebugger.standard_inject(Payload(after=self.draw_payload_after), instance.game_renderer, "draw")

    def init(self, instance: RaycastingGame):
        instance.key_map[pygame.K_n] = self.toggle_noclip
        instance.key_map[pygame.K_F3] = self.toggle_debug_info

    def start(self):
        self.init(self.instance)
        self.inject(self.instance)
