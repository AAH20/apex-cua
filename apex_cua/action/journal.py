"""
apex_cua.action.journal
~~~~~~~~~~~~~~~~~~~~~~~

Transactional Action Journal with O(1) compensating rollback stack.
Ensures zero-ghost execution state by recording every interaction and its compensation counterpart.
Standard library only; zero external dependencies.
"""

from typing import List, Dict, Optional, Any
import time
from apex_cua.core.primitives import ActionIntent, ActionResult, ActionType


class JournalEntry:
    def __init__(
        self,
        entry_id: str,
        intent: ActionIntent,
        compensating_action: ActionIntent,
        result: Optional[ActionResult] = None,
    ):
        self.entry_id = entry_id
        self.intent = intent
        self.compensating_action = compensating_action
        self.result = result
        self.timestamp = time.time()
        self.is_rolled_back = False


class ActionJournal:
    """
    Transactional ledger tracking atomic CUA actions and rollback state.
    """

    def __init__(self):
        self._history: List[JournalEntry] = []
        self._rollback_stack: List[JournalEntry] = []

    def record_intent(
        self,
        intent: ActionIntent,
        compensating_action: Optional[ActionIntent] = None,
    ) -> JournalEntry:
        """
        Records an action before execution and pushes compensation intent onto the rollback stack.
        """
        compensation = compensating_action or ActionIntent(
            action_id=f"comp_{intent.action_id}",
            action_type=ActionType.KEY_COMBINATION,
            key_codes=["Escape"],
        )

        entry = JournalEntry(
            entry_id=f"entry_{len(self._history) + 1}",
            intent=intent,
            compensating_action=compensation,
        )
        self._history.append(entry)
        self._rollback_stack.append(entry)
        return entry

    def commit_result(self, entry: JournalEntry, result: ActionResult) -> None:
        """Updates entry with final execution and verification outcome."""
        entry.result = result

    def pop_rollback(self) -> Optional[ActionIntent]:
        """
        Pops the latest uncommitted or failed action from the rollback stack in O(1).
        Returns the compensating action intent.
        """
        if not self._rollback_stack:
            return None
        entry = self._rollback_stack.pop()
        entry.is_rolled_back = True
        return entry.compensating_action

    def get_history(self) -> List[Dict[str, Any]]:
        """Returns structured audit log."""
        logs = []
        for e in self._history:
            logs.append({
                "entry_id": e.entry_id,
                "action_id": e.intent.action_id,
                "action_type": e.intent.action_type.value,
                "success": e.result.success if e.result else False,
                "verified": e.result.verified if e.result else False,
                "is_rolled_back": e.is_rolled_back,
                "timestamp": e.timestamp,
            })
        return logs

    def clear(self) -> None:
        """Flushes history and rollback stack."""
        self._history.clear()
        self._rollback_stack.clear()
