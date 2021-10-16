import pygame
from pygame.event import Event
from pygame.time import Clock
from pygame.surface import Surface
from pygame import Color

pygame.init()


class RaycastingGame:
    def __init__(self, background_colour: Color = (255, 255, 255)):
        self.background_colour = background_colour

        self.clock = Clock()
        self.running = False
        self.key_map = {
            pygame.K_ESCAPE: self.quit
        }

    def quit(self):
        self.running = False

    def process_events(self, events: list[Event]):
        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key in self.key_map.keys():
                    self.key_map[event.key]()

    def update(self):
        delta_time = self.clock.tick()
        self.process_events(pygame.event.get())

    def draw(self, surface: Surface):
        surface.fill(self.background_colour)

    def mainloop(self):
        window = pygame.display.set_mode((0, 0))

        self.running = True

        while self.running:
            self.update()
            self.draw(window)
            pygame.display.flip()


if __name__ == '__main__':
    game = RaycastingGame()

    game.mainloop()
