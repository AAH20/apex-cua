"""
apex_cua.core.action_contract
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Atomic Action Contracts with pre/post assertion verification and O(1) compensating rollback.
Eliminates blind GUI action loops by ensuring state transitions succeed before next step.
"""

from typing import Callable, Optional, Dict, Any, Tuple
import time
from apex_cua.core.primitives import ActionIntent, ActionResult, ActionType


class ActionContract:
    """
    Encapsulates an action intent with formal state transition assertions.
    """

    def __init__(
        self,
        intent: ActionIntent,
        pre_assertion: Optional[Callable[[Dict[str, Any]], bool]] = None,
        post_assertion: Optional[Callable[[Dict[str, Any]], bool]] = None,
        timeout_ms: float = 1500.0,
        compensating_action: Optional[ActionIntent] = None,
    ):
        self.intent = intent
        self.pre_assertion = pre_assertion or (lambda s: True)
        self.post_assertion = post_assertion or (lambda s: True)
        self.timeout_ms = timeout_ms
        self.compensating_action = compensating_action or ActionIntent(
            action_id=f"rollback_{intent.action_id}",
            action_type=ActionType.KEY_COMBINATION,
            key_codes=["Escape"],
        )

    def verify_pre(self, state: Dict[str, Any]) -> bool:
        try:
            return self.pre_assertion(state)
        except Exception:
            return False

    def verify_post(self, state: Dict[str, Any]) -> bool:
        try:
            return self.post_assertion(state)
        except Exception:
            return False


class ActionContractEngine:
    """
    Coordinates atomic contract execution, post-condition verification, and rollback.
    """

    def __init__(self):
        self.executed_contracts = 0
        self.verified_transitions = 0
        self.rollbacks_triggered = 0

    def validate_and_execute(
        self,
        contract: ActionContract,
        initial_state: Dict[str, Any],
        executor_fn: Callable[[ActionIntent], bool],
        poll_state_fn: Callable[[], Dict[str, Any]],
    ) -> ActionResult:
        """
        Executes action contract with atomic pre/post assertions and compensating rollback.
        """
        self.executed_contracts += 1
        t_start = time.perf_counter()
        pre_hash = str(initial_state.get("state_hash", "pre_hash_0"))

        # 1. Verify Pre-Condition
        if not contract.verify_pre(initial_state):
            t_elapsed_ms = (time.perf_counter() - t_start) * 1000.0
            return ActionResult(
                action_id=contract.intent.action_id,
                success=False,
                execution_latency_ms=round(t_elapsed_ms, 2),
                pre_state_hash=pre_hash,
                post_state_hash=pre_hash,
                verified=False,
                rolled_back=False,
                message="Pre-condition assertion failed: target element not ready",
            )

        # 2. Execute Virtual HID Action
        action_dispatched = executor_fn(contract.intent)
        if not action_dispatched:
            t_elapsed_ms = (time.perf_counter() - t_start) * 1000.0
            return ActionResult(
                action_id=contract.intent.action_id,
                success=False,
                execution_latency_ms=round(t_elapsed_ms, 2),
                pre_state_hash=pre_hash,
                post_state_hash=pre_hash,
                verified=False,
                rolled_back=False,
                message="Virtual HID event injection failed",
            )

        # 3. Await Post-Condition Transition with Timeout
        timeout_sec = contract.timeout_ms / 1000.0
        post_verified = False
        latest_state = initial_state

        deadline = time.time() + timeout_sec
        while time.time() <= deadline:
            latest_state = poll_state_fn()
            if contract.verify_post(latest_state):
                post_verified = True
                break
            time.sleep(0.01)  # 10ms poll interval

        post_hash = str(latest_state.get("state_hash", "post_hash_1"))

        # 4. Handle Post-Condition Failure via Compensating Action
        rolled_back = False
        if not post_verified:
            self.rollbacks_triggered += 1
            executor_fn(contract.compensating_action)
            rolled_back = True
            msg = f"Post-condition timed out after {contract.timeout_ms}ms; compensating action triggered"
        else:
            self.verified_transitions += 1
            msg = "Action and state transition successfully verified"

        t_elapsed_ms = (time.perf_counter() - t_start) * 1000.0

        return ActionResult(
            action_id=contract.intent.action_id,
            success=post_verified,
            execution_latency_ms=round(t_elapsed_ms, 2),
            pre_state_hash=pre_hash,
            post_state_hash=post_hash,
            verified=post_verified,
            rolled_back=rolled_back,
            message=msg,
        )
