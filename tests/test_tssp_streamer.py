"""
tests.test_tssp_streamer
~~~~~~~~~~~~~~~~~~~~~~~~

Unit tests for TSSPStreamer semantic event and micro-tile encoding at <12Kbps.
"""

import json
import unittest
from apex_cua.compositor.tssp_streamer import TSSPStreamer
from apex_cua.core.primitives import MacroTile, UIElementNode, BoundingBox


class TestTSSPStreamer(unittest.TestCase):
    def setUp(self):
        self.streamer = TSSPStreamer(client_id="test_streamer")

    def test_encode_packet(self):
        tile1 = MacroTile(
            tile_id="t_0_0",
            x=0,
            y=0,
            size=64,
            dhash_64bit=0x1234567890ABCDEF,
            raw_bytes=b"\x00" * 512,
        )
        focused = UIElementNode(
            element_id="btn_submit",
            role="AXButton",
            title="Submit Query",
            bounds=BoundingBox(10, 10, 100, 30),
        )

        packet_bytes = self.streamer.encode_packet(
            active_window_title="Cockpit Window",
            focused_element=focused,
            dirty_tiles=[tile1],
        )

        self.assertGreater(len(packet_bytes), 0)
        parsed = json.loads(packet_bytes.decode("utf-8"))
        self.assertEqual(parsed["proto"], "TSSP/1.0")
        self.assertEqual(parsed["seq"], 1)
        self.assertEqual(parsed["focused_id"], "btn_submit")
        self.assertEqual(len(parsed["tiles"]), 1)
        self.assertEqual(parsed["tiles"][0]["id"], "t_0_0")

    def test_bitrate_and_reduction(self):
        # Transmit 5 small packets
        for _ in range(5):
            self.streamer.encode_packet("Active Window", None, [])

        kbps = self.streamer.calculate_effective_bitrate_kbps(1.0)
        reduction = self.streamer.get_bandwidth_reduction_factor()

        # Wire bytes should be modest and bitrate within target
        self.assertLess(kbps, 100.0)
        self.assertGreater(reduction, 50.0)


if __name__ == "__main__":
    unittest.main()
