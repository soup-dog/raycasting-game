import numpy as np
from numpy.typing import NDArray


def angle_between_vectors(a: NDArray[float], b: NDArray[float]):
    # if a[0] == 0:
    #     print("a")
    #     a_angle = np.pi * 0.5 if a[1] >= 0 else np.pi * 1.5
    # else:
    #     print("else a")
    #     a_angle = np.arctan(a[1] / a[0])
    # if b[0] == 0:
    #     print("b")
    #     b_angle = np.pi * 0.5 if b[1] >= 0 else np.pi * 1.5
    # else:
    #     print("else b")
    #     b_angle = np.arctan(b[1] / b[0])
    #
    # print(a_angle, b_angle)
    #
    # return b_angle - a_angle

    return np.arccos(np.clip(np.inner(a, b) / (np.linalg.norm(a) * np.linalg.norm(b)), -1.0, 1.0))


def rotation_matrix(radians: float) -> NDArray[float]:
    return np.array([
        [np.cos(radians), -np.sin(radians)],
        [np.sin(radians), np.cos(radians)]
    ], dtype=float)
