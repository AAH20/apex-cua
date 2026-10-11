"""
tests.test_all_adapters
~~~~~~~~~~~~~~~~~~~~~~~

Unit tests for sovereign ecosystem adapters:
- ApexRigAdapter
- StarNetAdapter
- HeraldOSAdapter
- PaperclipAdapter
- TelepathyAdapter
- ImmuneKernelAdapter
- ApexFirmwareAdapter
"""

import unittest
from apex_cua.adapters import (
    ApexRigAdapter,
    StarNetAdapter,
    HeraldOSAdapter,
    PaperclipAdapter,
    TelepathyAdapter,
    ImmuneKernelAdapter,
    ApexFirmwareAdapter,
)


class TestAllAdapters(unittest.TestCase):
    def test_rig_adapter(self):
        adapter = ApexRigAdapter()
        self.assertTrue(adapter.is_available())
        res = adapter.sync_state({"verified_ratio": 0.99, "mean_latency_ms": 3.8})
        self.assertEqual(res["adapter"], "apex_rig")
        self.assertEqual(res["status"], "synchronized")

    def test_starnet_adapter(self):
        adapter = StarNetAdapter()
        self.assertTrue(adapter.is_available())
        res = adapter.sync_state({"effective_kbps": 8.5})
        self.assertEqual(res["adapter"], "starnet_mesh")
        self.assertEqual(res["peers_connected"], 2)

    def test_herald_adapter(self):
        adapter = HeraldOSAdapter()
        self.assertTrue(adapter.is_available())
        res = adapter.sync_state({"focused_element_id": "window_main"})
        self.assertEqual(res["adapter"], "herald_os")
        self.assertEqual(res["semantic_status"], "fused")

    def test_paperclip_adapter_governance(self):
        adapter = PaperclipAdapter(daily_action_budget=5)
        self.assertTrue(adapter.check_action_permitted("click"))

        # Consume 5 actions
        adapter.sync_state({"actions_dispatched": 5})
        self.assertFalse(adapter.check_action_permitted("click"))

    def test_telepathy_adapter(self):
        adapter = TelepathyAdapter()
        self.assertTrue(adapter.is_available())
        res = adapter.sync_state({})
        self.assertEqual(res["adapter"], "telepathy_bus")
        self.assertEqual(res["status"], "connected")

    def test_immune_adapter_guardrails(self):
        adapter = ImmuneKernelAdapter()
        # Safe action
        self.assertTrue(adapter.verify_action_safety("type_text", None, "git status"))
        # Destructive action blocked
        self.assertFalse(adapter.verify_action_safety("type_text", None, "rm -rf /"))
        self.assertEqual(adapter.mitigations_applied, 1)

    def test_firmware_adapter(self):
        adapter = ApexFirmwareAdapter()
        self.assertTrue(adapter.is_available())
        res = adapter.sync_state({"duration_ms": 2.0})
        self.assertEqual(res["adapter"], "apex_firmware")
        self.assertTrue(res["simd_acceleration_active"])


if __name__ == "__main__":
    unittest.main()
