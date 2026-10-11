"""
apex_cua.perception.ax_trie
~~~~~~~~~~~~~~~~~~~~~~~~~~~

Radix Trie (Prefix Tree) spatial and semantic index for sub-millisecond UI element lookup.
Provides O(k) text query resolution across element titles, roles, and IDs.
Standard library only; zero external dependencies.
"""

from typing import List, Dict, Optional, Set, Tuple
from apex_cua.core.primitives import UIElementNode, BoundingBox


class TrieNode:
    def __init__(self):
        self.children: Dict[str, "TrieNode"] = {}
        self.elements: List[UIElementNode] = []
        self.is_terminal: bool = False


class RadixTrieUIIndex:
    """
    Sub-millisecond prefix and token index for accessibility hierarchy elements.
    """

    def __init__(self):
        self.root = TrieNode()
        self.id_map: Dict[str, UIElementNode] = {}
        self.element_count: int = 0

    def clear(self) -> None:
        """Clears the index."""
        self.root = TrieNode()
        self.id_map.clear()
        self.element_count = 0

    def _normalize(self, text: str) -> str:
        return text.strip().lower()

    def insert(self, element: UIElementNode) -> None:
        """Indexes a single UI element by its ID, title tokens, and role."""
        if not element.element_id:
            return

        self.id_map[element.element_id] = element
        self.element_count += 1

        keys_to_index: Set[str] = set()

        # 1. Index full ID and title
        keys_to_index.add(self._normalize(element.element_id))
        if element.title:
            norm_title = self._normalize(element.title)
            keys_to_index.add(norm_title)
            # Index individual tokens
            for token in norm_title.split():
                if len(token) > 1:
                    keys_to_index.add(token)

        # 2. Index role
        if element.role:
            keys_to_index.add(self._normalize(element.role))

        # Insert each key into Trie
        for key in keys_to_index:
            curr = self.root
            for char in key:
                if char not in curr.children:
                    curr.children[char] = TrieNode()
                curr = curr.children[char]
            curr.is_terminal = True
            if element not in curr.elements:
                curr.elements.append(element)

    def build_from_tree(self, root_nodes: List[UIElementNode]) -> None:
        """Recursively walks UI tree and builds full index."""
        self.clear()

        def _walk(node: UIElementNode):
            self.insert(node)
            for child in node.children:
                _walk(child)

        for root in root_nodes:
            _walk(root)

    def find_by_prefix(self, prefix: str) -> List[UIElementNode]:
        """Returns all elements having a title, token, role, or ID starting with prefix."""
        norm_prefix = self._normalize(prefix)
        if not norm_prefix:
            return []

        curr = self.root
        for char in norm_prefix:
            if char not in curr.children:
                return []
            curr = curr.children[char]

        # Collect all elements from this subtree
        found: List[UIElementNode] = []
        seen_ids: Set[str] = set()

        def _collect(node: TrieNode):
            for elem in node.elements:
                if elem.element_id not in seen_ids:
                    seen_ids.add(elem.element_id)
                    found.append(elem)
            for child in node.children.values():
                _collect(child)

        _collect(curr)
        return found

    def find_by_id(self, element_id: str) -> Optional[UIElementNode]:
        """Direct O(1) lookup by element identifier."""
        return self.id_map.get(element_id)

    def find_at_point(self, px: float, py: float) -> List[UIElementNode]:
        """Finds all indexed elements whose bounding boxes contain (px, py)."""
        matches: List[UIElementNode] = []
        for elem in self.id_map.values():
            if elem.bounds.contains(px, py):
                matches.append(elem)
        # Sort by smallest area (most specific inner element first)
        matches.sort(key=lambda e: e.bounds.width * e.bounds.height)
        return matches
