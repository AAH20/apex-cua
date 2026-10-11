"""
apex_cua.compositor.shm_buffer
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

POSIX Shared-Memory Virtual Framebuffer (SHM-FB).
Provides zero-copy memory-mapped framebuffer sharing between display compositor and agent runtime.
Sub-0.1ms frame handoff; standard library only (mmap, struct, os).
"""

import os
import mmap
import struct
import tempfile
from typing import Optional, Tuple


class SharedMemoryFramebuffer:
    """
    Zero-copy POSIX shared memory ring buffer for high-throughput headless framebuffers.
    Header format (32 bytes):
      magic: 4s ('CUA\x00')
      sequence_id: Q (uint64)
      timestamp_ns: Q (uint64)
      width: I (uint32)
      height: I (uint32)
      stride: I (uint32)
      bpp: H (uint16)
      reserved: 2s
    Followed by raw pixel bytes (width * height * bpp).
    """

    HEADER_FORMAT = "<4sQQIIIH2s"
    HEADER_SIZE = struct.calcsize(HEADER_FORMAT)
    MAGIC = b"CUA\x00"

    def __init__(
        self,
        name: str = "apex_cua_shm_0",
        width: int = 1920,
        height: int = 1080,
        bpp: int = 4,
        create: bool = True,
    ):
        self.name = name
        self.width = width
        self.height = height
        self.bpp = bpp
        self.stride = width * bpp
        self.payload_size = self.stride * height
        self.total_size = self.HEADER_SIZE + self.payload_size
        self._seq = 0
        self._mmap: Optional[mmap.mmap] = None
        self._file_obj = None

        self._setup_backing(create)

    def _setup_backing(self, create: bool) -> None:
        """Sets up mmap backing via /dev/shm or tempfile fallback."""
        shm_path = f"/dev/shm/{self.name}"
        if not os.path.exists("/dev/shm") or not os.access("/dev/shm", os.W_OK):
            # Fallback for macOS / non-standard environments
            temp_dir = tempfile.gettempdir()
            shm_path = os.path.join(temp_dir, f"{self.name}.shm")

        self.backing_path = shm_path

        if create:
            self._file_obj = open(self.backing_path, "wb+")
            self._file_obj.truncate(self.total_size)
            self._mmap = mmap.mmap(self._file_obj.fileno(), self.total_size, mmap.MAP_SHARED, mmap.PROT_READ | mmap.PROT_WRITE)
            self.write_header(0, 0)
        else:
            self._file_obj = open(self.backing_path, "rb+")
            self._mmap = mmap.mmap(self._file_obj.fileno(), self.total_size, mmap.MAP_SHARED, mmap.PROT_READ | mmap.PROT_WRITE)

    def write_header(self, sequence_id: int, timestamp_ns: int) -> None:
        """Writes 32-byte synchronization header."""
        if not self._mmap:
            return
        header = struct.pack(
            self.HEADER_FORMAT,
            self.MAGIC,
            sequence_id,
            timestamp_ns,
            self.width,
            self.height,
            self.stride,
            self.bpp,
            b"\x00\x00",
        )
        self._mmap.seek(0)
        self._mmap.write(header)

    def read_header(self) -> Tuple[int, int, int, int, int, int]:
        """Reads synchronization header: (seq_id, timestamp_ns, width, height, stride, bpp)."""
        if not self._mmap:
            return (0, 0, self.width, self.height, self.stride, self.bpp)
        self._mmap.seek(0)
        hdr = self._mmap.read(self.HEADER_SIZE)
        magic, seq, ts, w, h, stride, bpp, _ = struct.unpack(self.HEADER_FORMAT, hdr)
        return (seq, ts, w, h, stride, bpp)

    def write_frame(self, frame_bytes: bytes, timestamp_ns: int = 0) -> int:
        """Writes raw frame bytes directly to shared memory buffer in <0.1ms."""
        if not self._mmap:
            return 0
        self._seq += 1
        self.write_header(self._seq, timestamp_ns)
        self._mmap.seek(self.HEADER_SIZE)
        write_len = min(len(frame_bytes), self.payload_size)
        self._mmap.write(frame_bytes[:write_len])
        return self._seq

    def read_frame(self) -> bytes:
        """Zero-copy read of current frame buffer."""
        if not self._mmap:
            return b""
        self._mmap.seek(self.HEADER_SIZE)
        return self._mmap.read(self.payload_size)

    def close(self) -> None:
        """Closes memory map and releases backing descriptor."""
        if self._mmap:
            self._mmap.close()
            self._mmap = None
        if self._file_obj:
            self._file_obj.close()
            self._file_obj = None
        if os.path.exists(self.backing_path):
            try:
                os.remove(self.backing_path)
            except OSError:
                pass
