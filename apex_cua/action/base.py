"""
apex_cua.action.base
~~~~~~~~~~~~~~~~~~~~

Abstract Virtual HID interface for low-latency native OS input dispatch.
Standard library only; zero external dependencies.
"""

from abc import ABC, abstractmethod
from typing import List


class BaseVirtualHID(ABC):
    """
    Abstract interface for native OS Virtual Human Interface Device (HID) event injection.
    """

    @abstractmethod
    def move_to(self, x: float, y: float) -> bool:
        """Positions virtual pointer at exact screen coordinates."""
        pass

    @abstractmethod
    def click(self, x: float, y: float) -> bool:
        """Injects primary mouse button down and up event."""
        pass

    @abstractmethod
    def double_click(self, x: float, y: float) -> bool:
        """Injects double click event."""
        pass

    @abstractmethod
    def right_click(self, x: float, y: float) -> bool:
        """Injects secondary mouse button click."""
        pass

    @abstractmethod
    def drag_and_drop(self, start_x: float, start_y: float, end_x: float, end_y: float) -> bool:
        """Performs atomic mouse drag and release sequence."""
        pass

    @abstractmethod
    def type_text(self, text: str) -> bool:
        """Injects keyboard character sequences."""
        pass

    @abstractmethod
    def key_combination(self, keys: List[str]) -> bool:
        """Injects modifier key combinations (e.g. ['Command', 'Z'] or ['Ctrl', 'C'])."""
        pass

    @abstractmethod
    def scroll(self, dx: int, dy: int) -> bool:
        """Injects scroll wheel deltas."""
        pass
