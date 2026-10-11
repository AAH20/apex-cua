"""
tests.test_full_pipeline
~~~~~~~~~~~~~~~~~~~~~~~~

Full end-to-end integration tests for ApexCUAOrchestrator.
Tests Tri-Modal perception hierarchy, atomic action execution, rollback, and TSSP streaming.
"""

import unittest
from apex_cua.orchestrator import ApexCUAOrchestrator
from apex_cua.core.primitives import (
    PerceptionMode,
    ActionType,
    ActionIntent,
    NormalizedPoint,
)


class TestFullPipeline(unittest.TestCase):
    def setUp(self):
        self.orch = ApexCUAOrchestrator(
            viewport_width=1920,
            viewport_height=1080,
            scale_factor=1.0,
            enable_headless=True,
            force_simulation=True,
        )

    def tearDown(self):
        self.orch.shutdown()

    def test_perception_tier0_native_match(self):
        # Query known item from mock tree
        res = self.orch.perceive_element("Deploy Sovereign Agent")
        self.assertTrue(res.target_found)
        self.assertEqual(res.mode, PerceptionMode.AX_NATIVE)
        self.assertEqual(res.tokens_consumed, 0)
        self.assertLess(res.latency_ms, 5.0)

    def test_perception_tier1_quadtree_fallback(self):
        # Query unknown item -> falls back to QuadTree frame differencing
        if self.orch.display:
            # Mutate display with dirty box
            self.orch.display.generate_pattern_frame(dirty_box=(300, 300, 100, 100))

        res = self.orch.perceive_element("NonExistentCustomCanvasElement")
        self.assertTrue(res.target_found)
        self.assertEqual(res.mode, PerceptionMode.LOCAL_VLM_CROP)
        self.assertGreater(len(res.delta_tiles), 0)
        self.assertLess(res.latency_ms, 60.0)

    def test_action_execution_success(self):
        intent = ActionIntent(
            action_id="pipeline_click_1",
            action_type=ActionType.CLICK,
            coords_normalized=NormalizedPoint(0.2, 0.2),
        )
        res = self.orch.execute_action(intent)
        self.assertTrue(res.success)
        self.assertTrue(res.verified)
        self.assertFalse(res.rolled_back)
        self.assertLess(res.execution_latency_ms, 20.0)

    def test_action_blocked_by_guardrail(self):
        intent = ActionIntent(
            action_id="bad_cmd_1",
            action_type=ActionType.TYPE_TEXT,
            text_payload="rm -rf /sys/kernel",
        )
        res = self.orch.execute_action(intent)
        self.assertFalse(res.success)
        self.assertIn("blocked by Agent-Immune-Kernel", res.message)

    def test_tssp_state_streaming(self):
        stream_bytes = self.orch.stream_state_tssp()
        self.assertGreater(len(stream_bytes), 0)
        kbps = self.orch.tssp_streamer.calculate_effective_bitrate_kbps(1.0)
        self.assertLess(kbps, 50.0)


if __name__ == "__main__":
    unittest.main()
