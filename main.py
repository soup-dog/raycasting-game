import pygame
from pygame.event import Event

pygame.init()


class RaycastingGame:
    def __init__(self):
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

    def mainloop(self):
        window = pygame.display.set_mode((0, 0))

        self.running = True

        while self.running:
            self.process_events(pygame.event.get())


if __name__ == '__main__':
    game = RaycastingGame()

    game.mainloop()
