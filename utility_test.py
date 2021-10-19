import unittest
from utility import angle_between_vectors
import numpy as np


class UtilityTest(unittest.TestCase):
    def test_angle_between_vectors(self):
        self.assertEqual(angle_between_vectors(np.array([1, 0]), np.array([1, 0])), np.radians(0))
        self.assertEqual(angle_between_vectors(np.array([1, 0]), np.array([0, 1])), np.radians(90))
        self.assertEqual(angle_between_vectors(np.array([1, 0]), np.array([-1, 0])), np.radians(180))
        self.assertEqual(angle_between_vectors(np.array([1, 0]), np.array([0, -1])), np.radians(90))


if __name__ == '__main__':
    unittest.main()
