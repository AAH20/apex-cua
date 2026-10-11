"""
apex_cua.compositor.headless_display
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Headless Virtual Display Compositor for Apex_CUA.
Manages virtual display resolutions, Wayland/Xvfb session lifecycles, and test pattern generation.
Standard library only; zero external dependencies.
"""

import time
from typing import Optional, Tuple
from apex_cua.compositor.shm_buffer import SharedMemoryFramebuffer


class HeadlessDisplayCompositor:
    """
    Manages a virtual display resolution mapped directly into a SharedMemoryFramebuffer.
    """

    def __init__(
        self,
        width: int = 1920,
        height: int = 1080,
        refresh_rate: int = 60,
        shm_name: str = "apex_cua_display_0",
    ):
        self.width = width
        self.height = height
        self.refresh_rate = refresh_rate
        self.shm_name = shm_name
        self.framebuffer = SharedMemoryFramebuffer(
            name=shm_name,
            width=width,
            height=height,
            bpp=4,
            create=True,
        )
        self.frame_count = 0
        self.is_active = True

    def generate_pattern_frame(self, dirty_box: Optional[Tuple[int, int, int, int]] = None) -> bytes:
        """
        Generates a synthetic 32-bit BGRA framebuffer for deterministic benchmarking.
        Optionally renders a mutated box (x, y, w, h) simulating a dynamic UI change.
        """
        # Fast synthetic buffer generation using repeated byte pattern
        total_pixels = self.width * self.height
        stride = self.width * 4

        # Base background: Dark slate (B=30, G=25, R=20, A=255)
        base_pixel = b"\x1e\x19\x14\xff"
        # 16-pixel block multiplication
        block_16 = base_pixel * 16
        blocks_needed = total_pixels // 16
        remainder = total_pixels % 16
        buffer_array = bytearray(block_16 * blocks_needed + base_pixel * remainder)

        # Mutate specific region if requested (e.g. simulated button click or popup)
        if dirty_box:
            bx, by, bw, bh = dirty_box
            highlight_pixel = b"\x00\xd7\xff\xff"  # Vibrant amber highlight
            for row in range(by, min(by + bh, self.height)):
                row_offset = row * stride
                for col in range(bx, min(bx + bw, self.width)):
                    px_offset = row_offset + (col * 4)
                    buffer_array[px_offset : px_offset + 4] = highlight_pixel

        frame_bytes = bytes(buffer_array)
        self.frame_count += 1
        self.framebuffer.write_frame(frame_bytes, timestamp_ns=time.time_ns())
        return frame_bytes

    def get_current_frame(self) -> bytes:
        """Retrieves raw framebuffer from shared memory."""
        return self.framebuffer.read_frame()

    def shutdown(self) -> None:
        """Shuts down virtual display and releases shared memory buffer."""
        self.is_active = False
        self.framebuffer.close()
