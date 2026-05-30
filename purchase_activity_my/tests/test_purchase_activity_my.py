# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Sep 2023

from lxml import etree

from .common import TestPurchaseActivityMyCommon


class TestPurchaseActivityMy(TestPurchaseActivityMyCommon):
    """Tests for purchase_activity_my module."""

    def test_01_purchase_order_list_view_fields(self):
        """Check list view exposes activity_my_ids in combined arch."""
        view = self.env.ref("purchase_activity_my.purchase_order_tree_view")
        view_info = self.env["purchase.order"].get_view(
            view_id=view.id,
            view_type="list",
        )
        arch = etree.fromstring(view_info["arch"].encode())
        field_names = [el.get("name") for el in arch.iter("field")]
        self.assertIn("activity_my_ids", field_names)

    def test_02_purchase_order_kanban_view_fields(self):
        """Check kanban view exposes custom activity_my fields."""
        view = self.env.ref("purchase_activity_my.purchase_order_kanban_view")
        view_info = self.env["purchase.order"].get_view(
            view_id=view.id,
            view_type="kanban",
        )
        arch = etree.fromstring(view_info["arch"].encode())
        field_names = [el.get("name") for el in arch.iter("field")]
        self.assertIn("activity_my_ids", field_names)
        self.assertIn("activity_my_state", field_names)
