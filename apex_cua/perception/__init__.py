"""
apex_cua.perception
~~~~~~~~~~~~~~~~~~~

Tri-Modal Perception Hierarchy for Apex_CUA:
- Tier 0: Direct Native Accessibility Tree (AXUIElement / AT-SPI, 0ms, 0 tokens)
- Tier 1: SIMD QuadTree Delta Tiles (<3ms, 0 tokens)
- Tier 2: 64x64 Micro-Tile Local VLM Crop (<8ms, ~16 tokens)
"""

from apex_cua.perception.base import BasePerceptionScanner
from apex_cua.perception.ax_scanner_macos import MacOSAccessibilityScanner
from apex_cua.perception.ax_scanner_linux import LinuxAccessibilityScanner
from apex_cua.perception.ax_trie import RadixTrieUIIndex
from apex_cua.perception.micro_tile_cropper import MicroTileCropper

__all__ = [
    "BasePerceptionScanner",
    "MacOSAccessibilityScanner",
    "LinuxAccessibilityScanner",
    "RadixTrieUIIndex",
    "MicroTileCropper",
]
