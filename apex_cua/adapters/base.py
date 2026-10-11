"""
apex_cua.adapters.base
~~~~~~~~~~~~~~~~~~~~~~

Base interface for sovereign ecosystem adapters.
Standard library only; zero external dependencies.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional


class BaseEcosystemAdapter(ABC):
    """
    Abstract interface for integrating Apex_CUA with sovereign AI ecosystem frameworks.
    """

    @abstractmethod
    def adapter_name(self) -> str:
        """Unique identifier of the ecosystem adapter."""
        pass

    @abstractmethod
    def is_available(self) -> bool:
        """Determines if the target ecosystem component is reachable or simulated."""
        pass

    @abstractmethod
    def sync_state(self, telemetry: Dict[str, Any]) -> Dict[str, Any]:
        """Exchanges telemetry and state with the target ecosystem kernel."""
        pass
