"""
tests.test_shm_buffer
~~~~~~~~~~~~~~~~~~~~~

Unit tests for SharedMemoryFramebuffer zero-copy memory-mapped operations.
"""

import unittest
from apex_cua.compositor.shm_buffer import SharedMemoryFramebuffer


class TestSharedMemoryFramebuffer(unittest.TestCase):
    def setUp(self):
        self.shm = SharedMemoryFramebuffer(
            name="test_shm_buffer_fb",
            width=320,
            height=240,
            bpp=4,
            create=True,
        )

    def tearDown(self):
        self.shm.close()

    def test_header_rw(self):
        seq, ts, w, h, stride, bpp = self.shm.read_header()
        self.assertEqual(w, 320)
        self.assertEqual(h, 240)
        self.assertEqual(stride, 320 * 4)
        self.assertEqual(bpp, 4)

    def test_write_and_read_frame(self):
        frame_data = b"\xaa\xbb\xcc\xdd" * (320 * 240)
        seq = self.shm.write_frame(frame_data, timestamp_ns=123456789)
        self.assertEqual(seq, 1)

        read_back = self.shm.read_frame()
        self.assertEqual(read_back, frame_data)

        # Sequence increment
        seq2 = self.shm.write_frame(frame_data, timestamp_ns=123456790)
        self.assertEqual(seq2, 2)


if __name__ == "__main__":
    unittest.main()
