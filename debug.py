from game import RaycastingGame
from agent import Agent
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


def no_op(*args, **kwargs):
    pass


class RaycastingGameDebugger(Debugger):
    DEBUG_MOD_KEY = pygame.KMOD_LSHIFT

    def __init__(self, instance: RaycastingGame):
        self.delta_time = 0
        self.font: SysFont = SysFont("", 30)
        self.instance: RaycastingGame = instance
        self.show_debug_info: bool = True
        self.player_take_hit: Callable = no_op

    def toggle_noclip(self, event):
        if event.mod == RaycastingGameDebugger.DEBUG_MOD_KEY and event.type == pygame.KEYDOWN:
            self.instance.player.clip = not self.instance.player.clip

    def toggle_godmode(self, event):
        if event.mod == RaycastingGameDebugger.DEBUG_MOD_KEY and event.type == pygame.KEYDOWN:
            # swap stored method with current take_hit method
            tmp = self.instance.player.take_hit
            self.instance.player.take_hit = self.player_take_hit
            self.player_take_hit = tmp

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

    def draw_map_payload_after(self, target: Callable, *args, **kwargs):
        surface = args[0]
        cell_size = int(surface.get_height() / target.__self__.map.shape[0])

        centre_offset_x = (surface.get_width() - cell_size * target.__self__.map.shape[0]) / 2

        for obj in self.instance.game_objects:
            if isinstance(obj, Agent) and obj.pathfinding:
                pygame.draw.circle(surface, (0, 0, 255), (obj.goal[0] * cell_size + centre_offset_x, obj.goal[1] * cell_size), 3)

    def inject(self, instance: RaycastingGame):
        RaycastingGameDebugger.standard_inject(Payload(self.update_payload_before), instance, "update")
        instance.draw_mode_map[RaycastingGame.DrawMode.GAME] = RaycastingGameDebugger.standard_inject(Payload(after=self.draw_payload_after), instance.game_renderer, "draw")
        instance.draw_mode_map[RaycastingGame.DrawMode.MAP] = RaycastingGameDebugger.standard_inject(Payload(after=self.draw_map_payload_after), instance.map_renderer, "draw")

    def init(self, instance: RaycastingGame):
        instance.key_map[pygame.K_n] = self.toggle_noclip
        instance.key_map[pygame.K_g] = self.toggle_godmode
        instance.key_map[pygame.K_F3] = self.toggle_debug_info

    def start(self):
        self.init(self.instance)
        self.inject(self.instance)
