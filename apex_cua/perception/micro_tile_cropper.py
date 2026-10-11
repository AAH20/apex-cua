"""
apex_cua.perception.micro_tile_cropper
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Sub-frame micro-tile extraction for Tier 2 local VLM verification (<8ms, ~16 tokens).
Crops 64x64 pixel windows directly from memory-mapped framebuffers without image libraries.
Standard library only; zero external dependencies.
"""

from typing import List, Dict, Optional, Tuple
from apex_cua.core.primitives import MacroTile, BoundingBox


class MicroTileCropper:
    """
    Extracts isolated 64x64 sub-regions from raw RGB/RGBA framebuffers for local VLM verification.
    """

    def __init__(self, target_tile_size: int = 64, bytes_per_pixel: int = 4):
        self.target_tile_size = target_tile_size
        self.bpp = bytes_per_pixel

    def crop_tile_bytes(
        self,
        framebuffer: bytes,
        frame_width: int,
        frame_height: int,
        start_x: int,
        start_y: int,
        crop_size: Optional[int] = None,
    ) -> bytes:
        """
        Extracts raw bytes for a square tile region from a linear framebuffer.
        """
        size = crop_size or self.target_tile_size
        stride = frame_width * self.bpp
        cropped_chunks = []

        for row in range(size):
            cur_y = start_y + row
            if cur_y >= frame_height:
                break
            line_start = (cur_y * stride) + (start_x * self.bpp)
            line_end = line_start + (size * self.bpp)
            if line_end <= len(framebuffer):
                cropped_chunks.append(framebuffer[line_start:line_end])
            elif line_start < len(framebuffer):
                cropped_chunks.append(framebuffer[line_start:])

        return b"".join(cropped_chunks)

    def extract_macro_tiles(
        self,
        framebuffer: bytes,
        frame_width: int,
        frame_height: int,
        dirty_tiles: List[MacroTile],
    ) -> List[MacroTile]:
        """
        Populates raw_bytes for each dirty macro-tile for downstream micro-VLM inspection.
        """
        populated = []
        for tile in dirty_tiles:
            raw = self.crop_tile_bytes(
                framebuffer=framebuffer,
                frame_width=frame_width,
                frame_height=frame_height,
                start_x=tile.x,
                start_y=tile.y,
                crop_size=tile.size,
            )
            tile.raw_bytes = raw
            populated.append(tile)
        return populated

    def compute_tile_luminance_histogram(self, tile_raw_bytes: bytes) -> List[int]:
        """
        Computes an 8-bin grayscale luminance histogram for rapid visual signature analysis.
        """
        bins = [0] * 8
        step = self.bpp
        for i in range(0, len(tile_raw_bytes), step):
            if i + 2 < len(tile_raw_bytes):
                r = tile_raw_bytes[i]
                g = tile_raw_bytes[i + 1]
                b = tile_raw_bytes[i + 2]
                lum = (r * 2 + g * 5 + b) >> 3
                bin_idx = min(7, lum // 32)
                bins[bin_idx] += 1
        return bins
