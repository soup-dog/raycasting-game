import io
from enum import IntEnum
import numpy as np
import numpy.typing
import struct
from typing import BinaryIO


class MapCell(IntEnum):
    EMPTY = 0
    WALL = 1


class MapHelper:
    @staticmethod
    def generate_random_map(shape) -> np.typing.NDArray[np.uint8]:
        # TODO: replace with something that actually generates a map
        return np.empty(shape, dtype=np.bool_).astype(np.uint8)  # placeholder

    @staticmethod
    def load_map(stream: BinaryIO) -> np.typing.NDArray[np.uint8]:
        shape = struct.unpack("!HH", stream.read(4))  # load map dimensions as two unsigned shorts
        arr = np.empty(shape, dtype=np.uint8)
        for row in range(shape[0]):
            for col in range(shape[1]):
                arr[row, col] = struct.unpack("!B", stream.read(1))[0]
        return arr

    @staticmethod
    def save_map(stream: BinaryIO, game_map: np.typing.NDArray[np.uint8]):
        stream.write(struct.pack("!HH", *game_map.shape))
        stream.write(game_map.tobytes())

    @staticmethod
    def load_map_file(path: str) -> np.typing.NDArray[np.uint8]:
        with open(path, "rb") as f:
            tmp = MapHelper.load_map(f)
        return tmp

    @staticmethod
    def save_map_file(path: str, game_map: np.typing.NDArray[np.uint8]):
        with open(path, "wb") as f:
            MapHelper.save_map(f, game_map)
