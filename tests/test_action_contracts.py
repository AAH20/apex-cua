"""
tests.test_action_contracts
~~~~~~~~~~~~~~~~~~~~~~~~~~~

Unit tests for ActionContract, ActionContractEngine, pre/post assertions, and compensating rollback.
"""

import unittest
from apex_cua.core.primitives import ActionIntent, ActionType, ActionResult
from apex_cua.core.action_contract import ActionContract, ActionContractEngine


class TestActionContracts(unittest.TestCase):
    def setUp(self):
        self.engine = ActionContractEngine()

    def test_successful_contract_execution(self):
        intent = ActionIntent(
            action_id="test_act_1",
            action_type=ActionType.CLICK,
        )
        contract = ActionContract(
            intent=intent,
            pre_assertion=lambda state: state.get("window_ready", True),
            post_assertion=lambda state: state.get("element_active", True),
        )

        executed_actions = []

        def executor(cmd):
            executed_actions.append(cmd)
            return True

        res = self.engine.validate_and_execute(
            contract=contract,
            initial_state={"window_ready": True},
            executor_fn=executor,
            poll_state_fn=lambda: {"element_active": True},
        )

        self.assertTrue(res.success)
        self.assertTrue(res.verified)
        self.assertFalse(res.rolled_back)
        self.assertEqual(len(executed_actions), 1)

    def test_pre_assertion_failure(self):
        intent = ActionIntent(action_id="test_act_fail_pre", action_type=ActionType.CLICK)
        contract = ActionContract(
            intent=intent,
            pre_assertion=lambda state: state.get("ready") is True,
        )

        res = self.engine.validate_and_execute(
            contract=contract,
            initial_state={"ready": False},
            executor_fn=lambda cmd: True,
            poll_state_fn=lambda: {},
        )

        self.assertFalse(res.success)
        self.assertFalse(res.verified)
        self.assertIn("Pre-condition assertion failed", res.message)

    def test_post_assertion_failure_and_rollback(self):
        intent = ActionIntent(action_id="test_act_fail_post", action_type=ActionType.TYPE_TEXT, text_payload="hello")
        contract = ActionContract(
            intent=intent,
            pre_assertion=lambda s: True,
            post_assertion=lambda s: s.get("text_entered") == "expected_val",
            timeout_ms=50.0,
        )

        dispatched = []

        def executor(cmd):
            dispatched.append(cmd.action_id)
            return True

        res = self.engine.validate_and_execute(
            contract=contract,
            initial_state={"state_hash": "pre_0"},
            executor_fn=executor,
            poll_state_fn=lambda: {"text_entered": "wrong_val"},
        )

        self.assertFalse(res.success)
        self.assertFalse(res.verified)
        self.assertTrue(res.rolled_back)
        # Should have executed the primary action AND the compensating rollback action
        self.assertIn("test_act_fail_post", dispatched)
        self.assertIn("rollback_test_act_fail_post", dispatched)


if __name__ == "__main__":
    unittest.main()
