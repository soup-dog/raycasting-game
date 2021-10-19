import numpy as np
from numpy.typing import NDArray
from utility import angle_between_vectors, rotation_matrix


class Player:
    def __init__(self, position: NDArray[float], direction: NDArray[float], camera_plane: NDArray[float] = None):
        self.position: NDArray[float] = position
        self.direction: NDArray[float] = direction
        if camera_plane is None:
            camera_plane = np.array([0, 0.66], dtype=float)
        self.camera_plane: NDArray[float] = camera_plane
        self.camera_plane_matrix: NDArray[float] = rotation_matrix(-angle_between_vectors(self.direction, self.camera_plane))

    def rotate(self, rotation_matrix: NDArray[float]):
        self.direction = np.dot(self.direction, rotation_matrix)
        # self.camera_plane = np.dot(self.camera_plane, rotation_matrix)
        self.camera_plane = np.dot(self.direction, self.camera_plane_matrix)

    def set_direction(self, direction: NDArray[float]):
        self.direction = direction
        self.camera_plane = np.dot(self.direction, self.camera_plane_matrix)