"""
apex_cua.adapters
~~~~~~~~~~~~~~~~~

Sovereign ecosystem adapters for Apex_CUA:
- ApexRigAdapter (apex-rig)
- StarNetAdapter (StarNet)
- HeraldOSAdapter (Herald OS)
- PaperclipAdapter (hermes-paperclip-adapter)
- TelepathyAdapter (agent-telepathy-bus)
- ImmuneKernelAdapter (agent-immune-kernel)
- ApexFirmwareAdapter (apex-firmware)
"""

from apex_cua.adapters.base import BaseEcosystemAdapter
from apex_cua.adapters.rig_adapter import ApexRigAdapter
from apex_cua.adapters.starnet_adapter import StarNetAdapter
from apex_cua.adapters.herald_adapter import HeraldOSAdapter
from apex_cua.adapters.paperclip_adapter import PaperclipAdapter
from apex_cua.adapters.telepathy_adapter import TelepathyAdapter
from apex_cua.adapters.immune_adapter import ImmuneKernelAdapter
from apex_cua.adapters.firmware_adapter import ApexFirmwareAdapter

__all__ = [
    "BaseEcosystemAdapter",
    "ApexRigAdapter",
    "StarNetAdapter",
    "HeraldOSAdapter",
    "PaperclipAdapter",
    "TelepathyAdapter",
    "ImmuneKernelAdapter",
    "ApexFirmwareAdapter",
]
