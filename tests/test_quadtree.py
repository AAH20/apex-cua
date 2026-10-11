"""
tests.test_quadtree
~~~~~~~~~~~~~~~~~~~

Unit tests for SpatialQuadTree and 64-bit dHash perceptual differencing.
"""

import unittest
from apex_cua.core.quadtree import SpatialQuadTree
from apex_cua.core.primitives import MacroTile


class TestSpatialQuadTree(unittest.TestCase):
    def setUp(self):
        self.tree = SpatialQuadTree(viewport_width=1920, viewport_height=1080, tile_size=64)

    def test_grid_dimensions(self):
        # 1920 / 64 = 30 cols; 1080 / 64 = 16.875 -> 17 rows
        self.assertEqual(self.tree.cols, 30)
        self.assertEqual(self.tree.rows, 17)
        self.assertEqual(self.tree.total_tiles, 30 * 17)

    def test_dhash_identical_buffers(self):
        # 64x64 RGBA dummy tile (all black)
        buffer = b"\x00\x00\x00\xff" * (1920 * 1080)
        hash1 = self.tree.compute_dhash_64bit(buffer, 1920 * 4, 0, 0)
        hash2 = self.tree.compute_dhash_64bit(buffer, 1920 * 4, 0, 0)
        self.assertEqual(hash1, hash2)

    def test_find_dirty_tiles_and_pruning(self):
        base_frame = b"\x1e\x1e\x1e\xff" * (1920 * 1080)

        # First scan marks all tiles as initial (dirty)
        dirty_first = self.tree.find_dirty_tiles(base_frame)
        self.assertEqual(len(dirty_first), self.tree.total_tiles)

        # Second scan with identical frame should detect 0 dirty tiles (100% pruning)
        dirty_second = self.tree.find_dirty_tiles(base_frame)
        self.assertEqual(len(dirty_second), 0)
        pruning = self.tree.get_pruning_ratio(len(dirty_second))
        self.assertEqual(pruning, 100.0)

        # Mutate a single tile (e.g. at (0, 0))
        mutated_frame = bytearray(base_frame)
        # Fill first tile with bright gradient
        for y in range(64):
            for x in range(64):
                offset = (y * 1920 * 4) + (x * 4)
                mutated_frame[offset : offset + 4] = b"\xff\xff\x00\xff"

        dirty_third = self.tree.find_dirty_tiles(bytes(mutated_frame))
        self.assertGreaterEqual(len(dirty_third), 1)
        self.assertLessEqual(len(dirty_third), 4)

        # Pruning ratio must exceed 96%
        pruning_ratio = self.tree.get_pruning_ratio(len(dirty_third))
        self.assertGreaterEqual(pruning_ratio, 96.0)


if __name__ == "__main__":
    unittest.main()
