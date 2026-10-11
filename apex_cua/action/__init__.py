"""
apex_cua.action
~~~~~~~~~~~~~~~

Virtual HID injectors, coordinate normalizers, and transactional action journals for Apex_CUA.
"""

from apex_cua.action.base import BaseVirtualHID
from apex_cua.action.vhid_macos import MacOSVirtualHID
from apex_cua.action.vhid_linux import LinuxVirtualHID
from apex_cua.action.coord_normalizer import CoordinateNormalizer
from apex_cua.action.journal import ActionJournal, JournalEntry

__all__ = [
    "BaseVirtualHID",
    "MacOSVirtualHID",
    "LinuxVirtualHID",
    "CoordinateNormalizer",
    "ActionJournal",
    "JournalEntry",
]
