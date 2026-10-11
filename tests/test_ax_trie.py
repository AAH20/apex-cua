"""
tests.test_ax_trie
~~~~~~~~~~~~~~~~~~

Unit tests for RadixTrieUIIndex prefix lookups and spatial spatial containment queries.
"""

import unittest
from apex_cua.perception.ax_trie import RadixTrieUIIndex
from apex_cua.core.primitives import UIElementNode, BoundingBox


class TestRadixTrieUIIndex(unittest.TestCase):
    def setUp(self):
        self.trie = RadixTrieUIIndex()
        self.node_btn = UIElementNode(
            element_id="ax_btn_save",
            role="AXButton",
            title="Save Document",
            bounds=BoundingBox(100.0, 100.0, 80.0, 30.0),
        )
        self.node_input = UIElementNode(
            element_id="ax_txt_name",
            role="AXTextField",
            title="File Name Input",
            bounds=BoundingBox(100.0, 150.0, 200.0, 30.0),
        )
        self.trie.insert(self.node_btn)
        self.trie.insert(self.node_input)

    def test_lookup_by_id(self):
        found = self.trie.find_by_id("ax_btn_save")
        self.assertIsNotNone(found)
        self.assertEqual(found.title, "Save Document")

    def test_lookup_by_prefix(self):
        # By title token "Save"
        res_save = self.trie.find_by_prefix("sav")
        self.assertEqual(len(res_save), 1)
        self.assertEqual(res_save[0].element_id, "ax_btn_save")

        # By title token "Document"
        res_doc = self.trie.find_by_prefix("doc")
        self.assertEqual(len(res_doc), 1)
        self.assertEqual(res_doc[0].element_id, "ax_btn_save")

        # By role "AXButton"
        res_btn = self.trie.find_by_prefix("axbutton")
        self.assertEqual(len(res_btn), 1)

    def test_find_at_point(self):
        # Point inside button
        elems = self.trie.find_at_point(120.0, 110.0)
        self.assertEqual(len(elems), 1)
        self.assertEqual(elems[0].element_id, "ax_btn_save")

        # Point inside input
        elems2 = self.trie.find_at_point(150.0, 160.0)
        self.assertEqual(len(elems2), 1)
        self.assertEqual(elems2[0].element_id, "ax_txt_name")

        # Point outside both
        elems3 = self.trie.find_at_point(500.0, 500.0)
        self.assertEqual(len(elems3), 0)


if __name__ == "__main__":
    unittest.main()
