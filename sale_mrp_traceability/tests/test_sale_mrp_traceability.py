# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Sep 2023

from lxml import etree

from .common import TestSaleMrpTraceabilityCommon


class TestSaleMrpTraceability(TestSaleMrpTraceabilityCommon):
    """Tests for sale_mrp_traceability module."""

    def test_01_sale_order_form_view_has_move_ids(self):
        """Check that move_ids field is present in sale order form arch when user
        has mrp traceability group."""
        view_info = self.env["sale.order"].get_view(view_type="form")
        arch = etree.fromstring(view_info["arch"].encode())
        field_names = [el.get("name") for el in arch.iter("field")]
        self.assertIn("move_ids", field_names)

    def test_02_stock_move_list_view_fields(self):
        """Check that expected fields are present in the custom stock move list view."""
        view = self.env.ref("sale_mrp_traceability.stock_move_tree_view")
        view_info = self.env["stock.move"].get_view(view_id=view.id, view_type="list")
        arch = etree.fromstring(view_info["arch"].encode())
        field_names = [el.get("name") for el in arch.iter("field")]
        self.assertIn("product_id", field_names)
        self.assertIn("pick_status", field_names)
        self.assertIn("state", field_names)
        self.assertIn("action_view_created_item_visible", field_names)
