"""
apex_cua.perception.base
~~~~~~~~~~~~~~~~~~~~~~~~

Base perception interfaces and abstract scanner contracts for Apex_CUA.
Standard library only; zero external dependencies.
"""

from abc import ABC, abstractmethod
from typing import List, Optional, Dict, Any
from apex_cua.core.primitives import UIElementNode, BoundingBox


class BasePerceptionScanner(ABC):
    """
    Abstract interface for native OS accessibility tree scanners (Tier 0).
    """

    @abstractmethod
    def scan_hierarchy(self) -> List[UIElementNode]:
        """Scans the active desktop/window and returns root UI elements."""
        pass

    @abstractmethod
    def get_focused_element(self) -> Optional[UIElementNode]:
        """Returns the currently focused UI element, if any."""
        pass

    @abstractmethod
    def find_elements_by_role(self, role: str) -> List[UIElementNode]:
        """Finds all visible elements matching the specified accessibility role."""
        pass

    @abstractmethod
    def find_elements_by_title(self, query: str, exact: bool = False) -> List[UIElementNode]:
        """Searches UI hierarchy for elements matching the specified label or title."""
        pass
