"""
tests.test_coord_normalizer
~~~~~~~~~~~~~~~~~~~~~~~~~~~

Unit tests for CoordinateNormalizer affine transformations and DPI scaling.
"""

import unittest
from apex_cua.action.coord_normalizer import CoordinateNormalizer
from apex_cua.core.primitives import NormalizedPoint, BoundingBox


class TestCoordinateNormalizer(unittest.TestCase):
    def test_standard_1080p_normalization(self):
        norm = CoordinateNormalizer(viewport_width=1920.0, viewport_height=1080.0, scale_factor=1.0)

        # Center point
        p_norm = norm.to_normalized(960.0, 540.0)
        self.assertAlmostEqual(p_norm.x_norm, 0.5, places=3)
        self.assertAlmostEqual(p_norm.y_norm, 0.5, places=3)

        # Invert back to screen
        sx, sy = norm.to_screen(p_norm)
        self.assertAlmostEqual(sx, 960.0, places=1)
        self.assertAlmostEqual(sy, 540.0, places=1)

    def test_retina_2x_scaling(self):
        # 2x scale: effective viewport is 3840x2160
        norm = CoordinateNormalizer(viewport_width=1920.0, viewport_height=1080.0, scale_factor=2.0)

        p_norm = norm.to_normalized(1920.0, 1080.0)
        self.assertAlmostEqual(p_norm.x_norm, 0.5, places=3)
        self.assertAlmostEqual(p_norm.y_norm, 0.5, places=3)

        sx, sy = norm.to_screen(p_norm)
        self.assertAlmostEqual(sx, 1920.0, places=1)
        self.assertAlmostEqual(sy, 1080.0, places=1)

    def test_clamping_out_of_bounds(self):
        norm = CoordinateNormalizer(viewport_width=1920.0, viewport_height=1080.0)

        p_neg = norm.to_normalized(-100.0, -50.0)
        self.assertEqual(p_neg.x_norm, 0.0)
        self.assertEqual(p_neg.y_norm, 0.0)

        p_over = norm.to_normalized(3000.0, 2000.0)
        self.assertEqual(p_over.x_norm, 1.0)
        self.assertEqual(p_over.y_norm, 1.0)

    def test_normalize_box(self):
        norm = CoordinateNormalizer(viewport_width=1000.0, viewport_height=1000.0)
        box = BoundingBox(x=100.0, y=200.0, width=400.0, height=300.0)
        tl, br = norm.normalize_box(box)

        self.assertAlmostEqual(tl.x_norm, 0.1)
        self.assertAlmostEqual(tl.y_norm, 0.2)
        self.assertAlmostEqual(br.x_norm, 0.5)
        self.assertAlmostEqual(br.y_norm, 0.5)


if __name__ == "__main__":
    unittest.main()
