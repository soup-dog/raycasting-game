# numpy
import numpy as np
# standard
from enum import IntEnum
import struct
# typing
from typing import BinaryIO
from numpy.typing import NDArray


Map = NDArray[np.uint8]


class MapCell(IntEnum):
    EMPTY = 0
    WALL = 1


class MapHelper:
    @staticmethod
    def generate_random_map(shape) -> Map:
        # TODO: replace with something that actually generates a map
        return np.empty(shape, dtype=np.bool_).astype(np.uint8)  # placeholder

    @staticmethod
    def load_map(stream: BinaryIO) -> Map:
        shape = struct.unpack("!HH", stream.read(4))  # load map dimensions as two unsigned shorts
        arr = np.empty(shape, dtype=np.uint8)
        for row in range(shape[0]):
            for col in range(shape[1]):
                arr[row, col] = struct.unpack("!B", stream.read(1))[0]
        return arr

    @staticmethod
    def save_map(stream: BinaryIO, game_map: Map):
        stream.write(struct.pack("!HH", *game_map.shape))  # write dimensions as two unsigned shorts
        stream.write(game_map.tobytes())  # dump map contents

    @staticmethod
    def load_map_file(path: str) -> Map:
        with open(path, "rb") as f:
            tmp = MapHelper.load_map(f)
        return tmp

    @staticmethod
    def save_map_file(path: str, game_map: Map):
        with open(path, "wb") as f:
            MapHelper.save_map(f, game_map)
