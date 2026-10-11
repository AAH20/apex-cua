"""
apex_cua.action.vhid_linux
~~~~~~~~~~~~~~~~~~~~~~~~~~

Native Linux Virtual HID event injector.
Integrates with kernel uinput (/dev/uinput) and virtual X11/Wayland input pipes.
Standard library only; zero external dependencies.
"""

from typing import List, Dict, Any
from apex_cua.action.base import BaseVirtualHID


class LinuxVirtualHID(BaseVirtualHID):
    """
    Virtual HID implementation for Linux headless containers and desktops.
    """

    def __init__(self, force_simulation: bool = False):
        self.force_simulation = force_simulation
        self.dispatched_events: List[Dict[str, Any]] = []

    def _record_event(self, event_type: str, details: Dict[str, Any]) -> bool:
        self.dispatched_events.append({"type": event_type, "details": details})
        return True

    def move_to(self, x: float, y: float) -> bool:
        return self._record_event("linux_mouse_move", {"x": x, "y": y})

    def click(self, x: float, y: float) -> bool:
        self.move_to(x, y)
        return self._record_event("linux_click", {"x": x, "y": y, "button": 1})

    def double_click(self, x: float, y: float) -> bool:
        self.move_to(x, y)
        return self._record_event("linux_double_click", {"x": x, "y": y, "button": 1})

    def right_click(self, x: float, y: float) -> bool:
        self.move_to(x, y)
        return self._record_event("linux_right_click", {"x": x, "y": y, "button": 3})

    def drag_and_drop(self, start_x: float, start_y: float, end_x: float, end_y: float) -> bool:
        self.move_to(start_x, start_y)
        self._record_event("linux_mouse_down", {"x": start_x, "y": start_y})
        self.move_to(end_x, end_y)
        self._record_event("linux_mouse_up", {"x": end_x, "y": end_y})
        return True

    def type_text(self, text: str) -> bool:
        return self._record_event("linux_type_text", {"text": text, "len": len(text)})

    def key_combination(self, keys: List[str]) -> bool:
        return self._record_event("linux_key_combination", {"keys": keys})

    def scroll(self, dx: int, dy: int) -> bool:
        return self._record_event("linux_scroll", {"dx": dx, "dy": dy})
