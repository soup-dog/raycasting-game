import unittest
import numpy as np
import io
from game_map import MapHelper


class MapHelperTest(unittest.TestCase):
    def test_load(self):
        loaded_map = MapHelper.load_map(io.BytesIO(bytes([0, 4, 0, 4, 0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15])))
        actual = np.arange(16, dtype=np.uint8).reshape((4, 4))
        self.assertTrue(np.array_equal(loaded_map, actual))

    def test_save(self):
        destination_stream = io.BytesIO()
        MapHelper.save_map(destination_stream, np.arange(9, dtype=np.uint8).reshape((3, 3)))
        actual = bytes([0, 3, 0, 3, 0, 1, 2, 3, 4, 5, 6, 7, 8])
        self.assertEqual(destination_stream.getvalue(), actual)


if __name__ == '__main__':
    unittest.main()
