from __future__ import annotations

import numpy as np
from vector import Vector2


def angle_between_vectors(a: Vector2, b: Vector2):
    return np.arccos(np.clip(np.inner(a, b) / (np.linalg.norm(a) * np.linalg.norm(b)), -1.0, 1.0))


def rotation_matrix(radians: float) -> Vector2:
    return np.array([
        [np.cos(radians), -np.sin(radians)],
        [np.sin(radians), np.cos(radians)]
    ], dtype=float)


def magnitude_2d(vector2: Vector2) -> float:
    return np.sqrt(vector2[0] * vector2[0] + vector2[1] * vector2[1])  # faster than np.linalg.norm(x) or np.sqrt(x.dot(x))
