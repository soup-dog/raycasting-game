# standard
from abc import ABC, abstractmethod
# project
from game_object import GameObject


class Item(GameObject, ABC):
    @abstractmethod
    def can_pickup(self) -> bool:
        raise NotImplementedError()

    @abstractmethod
    def pickup(self):
        raise NotImplementedError()

    def try_pickup(self):
        if self.can_pickup():
            self.pickup()
