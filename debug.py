from game import RaycastingGame
from typing import Callable
import pygame
from pygame.freetype import SysFont


pygame.init()


PayloadMethod = Callable[[Callable, ...], None]


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
    def standard_inject(payload: Payload, instance: object, target_name: str):
        target = getattr(instance, target_name)

        def injection(*args, **kwargs):
            payload.before(target, *args, **kwargs)
            result = target(*args, **kwargs)
            payload.after(target, *args, **kwargs)
            return result
        setattr(instance, target_name, injection)


class RaycastingGameDebugger(Debugger):
    def __init__(self):
        self.delta_time = 0
        self.font: SysFont = SysFont("", 30)

    def update_payload_before(self, target: Callable, *args, **kwargs):
        self.delta_time = args[0]

    def draw_payload_after(self, target: Callable, *args, **kwargs):
        surface = args[0]
        self.font.render_to(surface, (0, 0), str(1 / self.delta_time))

    def inject(self, instance: RaycastingGame):
        RaycastingGameDebugger.standard_inject(Payload(self.update_payload_before), instance, "update")
        RaycastingGameDebugger.standard_inject(Payload(after=self.draw_payload_after), instance, "draw")
