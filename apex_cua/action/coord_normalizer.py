"""
apex_cua.action.coord_normalizer
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Sub-pixel invariant affine coordinate normalizer.
Maps arbitrary display resolutions and DPI scalings (1x, 2x Retina, 4x) to unit space [0.0, 1.0].
Guarantees resolution-independent action execution across heterogeneous agent environments.
Standard library only; zero external dependencies.
"""

from typing import Tuple
from apex_cua.core.primitives import NormalizedPoint, BoundingBox


class CoordinateNormalizer:
    """
    Affine transformation engine for resolution-invariant spatial coordinate mapping.
    """

    def __init__(
        self,
        viewport_width: float = 1920.0,
        viewport_height: float = 1080.0,
        scale_factor: float = 1.0,
        offset_x: float = 0.0,
        offset_y: float = 0.0,
    ):
        self.width = float(viewport_width)
        self.height = float(viewport_height)
        self.scale_factor = float(scale_factor)
        self.offset_x = float(offset_x)
        self.offset_y = float(offset_y)

    def to_normalized(self, screen_x: float, screen_y: float) -> NormalizedPoint:
        """
        Transforms absolute screen coordinates to unit space [0.0, 1.0].
        Clamps to valid unit bounds.
        """
        # Remove viewport offset and normalize by scaled dimensions
        effective_w = self.width * self.scale_factor
        effective_h = self.height * self.scale_factor

        adj_x = screen_x - self.offset_x
        adj_y = screen_y - self.offset_y

        norm_x = adj_x / effective_w if effective_w > 0 else 0.0
        norm_y = adj_y / effective_h if effective_h > 0 else 0.0

        clamped_x = max(0.0, min(1.0, norm_x))
        clamped_y = max(0.0, min(1.0, norm_y))

        return NormalizedPoint(x_norm=round(clamped_x, 6), y_norm=round(clamped_y, 6))

    def to_screen(self, normalized: NormalizedPoint) -> Tuple[float, float]:
        """
        Transforms normalized unit point [0.0, 1.0] back to physical screen coordinates.
        """
        effective_w = self.width * self.scale_factor
        effective_h = self.height * self.scale_factor

        phys_x = (normalized.x_norm * effective_w) + self.offset_x
        phys_y = (normalized.y_norm * effective_h) + self.offset_y

        return (round(phys_x, 2), round(phys_y, 2))

    def normalize_box(self, box: BoundingBox) -> Tuple[NormalizedPoint, NormalizedPoint]:
        """
        Returns normalized top-left and bottom-right points for a BoundingBox.
        """
        p_top_left = self.to_normalized(box.x, box.y)
        p_bottom_right = self.to_normalized(box.x + box.width, box.y + box.height)
        return (p_top_left, p_bottom_right)
