import numpy as np
from numpy.typing import NDArray


def angle_between_vectors(a: NDArray[float], b: NDArray[float]):
    return np.arccos(np.clip(np.inner(a, b) / (np.linalg.norm(a) * np.linalg.norm(b)), -1.0, 1.0))


def rotation_matrix(radians: float) -> NDArray[float]:
    return np.array([
        [np.cos(radians), -np.sin(radians)],
        [np.sin(radians), np.cos(radians)]
    ], dtype=float)


def magnitude_2d(vector2: NDArray[float]) -> float:
    return np.sqrt(vector2[0] * vector2[0] + vector2[1] * vector2[1])  # faster than np.linalg.norm(x) or np.sqrt(x.dot(x))
