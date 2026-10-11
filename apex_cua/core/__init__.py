"""
apex_cua.core
~~~~~~~~~~~~~

Core primitives, quadtree spatial index, and action contracts for Apex_CUA.
"""

from apex_cua.core.primitives import (
    PerceptionMode,
    ActionType,
    BoundingBox,
    NormalizedPoint,
    UIElementNode,
    MacroTile,
    PerceptionResult,
    ActionIntent,
    ActionResult,
    TSSPEvent,
)
from apex_cua.core.quadtree import SpatialQuadTree
from apex_cua.core.action_contract import ActionContract, ActionContractEngine

__all__ = [
    "PerceptionMode",
    "ActionType",
    "BoundingBox",
    "NormalizedPoint",
    "UIElementNode",
    "MacroTile",
    "PerceptionResult",
    "ActionIntent",
    "ActionResult",
    "TSSPEvent",
    "SpatialQuadTree",
    "ActionContract",
    "ActionContractEngine",
]
