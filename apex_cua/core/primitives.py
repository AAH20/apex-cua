"""
apex_cua.core.primitives
~~~~~~~~~~~~~~~~~~~~~~~~

Core domain primitives, bounding box geometry, and telemetry schemas for Apex_CUA.
Standard library only; zero external dependencies.
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Optional, Any, Tuple
import time


class PerceptionMode(str, Enum):
    AX_NATIVE = "ax_native"           # Tier 0: Direct accessibility API (0ms, 0 tokens)
    QUADTREE_DELTA = "quadtree_delta" # Tier 1: SIMD dHash tile delta (<3ms, 0 tokens)
    LOCAL_VLM_CROP = "local_vlm_crop" # Tier 2: 64x64 micro-tile local inference (<8ms, ~16 tokens)


class ActionType(str, Enum):
    CLICK = "click"
    DOUBLE_CLICK = "double_click"
    RIGHT_CLICK = "right_click"
    DRAG_AND_DROP = "drag_and_drop"
    TYPE_TEXT = "type_text"
    KEY_COMBINATION = "key_combination"
    SCROLL = "scroll"
    WAIT_FOR_ELEMENT = "wait_for_element"


@dataclass(frozen=True)
class BoundingBox:
    x: float
    y: float
    width: float
    height: float

    def contains(self, px: float, py: float) -> bool:
        return self.x <= px <= (self.x + self.width) and self.y <= py <= (self.y + self.height)

    def center(self) -> Tuple[float, float]:
        return (self.x + self.width / 2.0, self.y + self.height / 2.0)


@dataclass(frozen=True)
class NormalizedPoint:
    x_norm: float  # In [0.0, 1.0]
    y_norm: float  # In [0.0, 1.0]


@dataclass
class UIElementNode:
    element_id: str
    role: str                          # e.g., "AXButton", "AXTextField", "button", "input"
    title: str = ""
    bounds: BoundingBox = field(default_factory=lambda: BoundingBox(0, 0, 0, 0))
    is_enabled: bool = True
    is_focused: bool = False
    attributes: Dict[str, Any] = field(default_factory=dict)
    children: List["UIElementNode"] = field(default_factory=list)


@dataclass
class MacroTile:
    tile_id: str
    x: int
    y: int
    size: int = 64
    dhash_64bit: int = 0
    is_dirty: bool = False
    raw_bytes: bytes = b""


@dataclass
class PerceptionResult:
    mode: PerceptionMode
    target_found: bool
    element_node: Optional[UIElementNode]
    bounding_box: Optional[BoundingBox]
    delta_tiles: List[MacroTile] = field(default_factory=list)
    latency_ms: float = 0.0
    tokens_consumed: int = 0


@dataclass
class ActionIntent:
    action_id: str
    action_type: ActionType
    target_element_id: Optional[str] = None
    coords_normalized: Optional[NormalizedPoint] = None
    text_payload: str = ""
    key_codes: List[str] = field(default_factory=list)
    timeout_ms: float = 1500.0


@dataclass
class ActionResult:
    action_id: str
    success: bool
    execution_latency_ms: float
    pre_state_hash: str
    post_state_hash: str
    verified: bool
    rolled_back: bool = False
    message: str = ""
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class TSSPEvent:
    event_type: str
    timestamp_us: int
    active_window: str
    focused_element_id: Optional[str]
    delta_tile_count: int
    payload_bytes_size: int
    metadata: Dict[str, Any] = field(default_factory=dict)
