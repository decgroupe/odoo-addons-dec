# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Sep 2023

from lxml import etree

from .common import TestSaleActivityMyCommon


class TestSaleActivityMy(TestSaleActivityMyCommon):
    """Tests for the sale_activity_my module."""

    def test_01_quotation_list_view_fields(self):
        """Check activity_my fields are present in quotation list view arch."""
        view_info = self.SaleOrder.get_view(
            view_id=self.quotation_tree_view.id, view_type="list"
        )
        arch = etree.fromstring(view_info["arch"].encode())
        field_names = [el.get("name") for el in arch.iter("field")]
        self.assertIn("activity_my_ids", field_names)
        self.assertIn("activity_my_date_deadline", field_names)

    def test_02_order_list_view_fields(self):
        """Check activity_my fields are present in order list view arch."""
        view_info = self.SaleOrder.get_view(
            view_id=self.order_tree_view.id, view_type="list"
        )
        arch = etree.fromstring(view_info["arch"].encode())
        field_names = [el.get("name") for el in arch.iter("field")]
        self.assertIn("activity_my_ids", field_names)
        self.assertIn("activity_my_date_deadline", field_names)

    def test_03_order_kanban_view_fields(self):
        """Check activity_my fields are present in order kanban view arch."""
        view_info = self.SaleOrder.get_view(
            view_id=self.order_kanban_view.id, view_type="kanban"
        )
        arch = etree.fromstring(view_info["arch"].encode())
        field_names = [el.get("name") for el in arch.iter("field")]
        self.assertIn("activity_my_ids", field_names)
        self.assertIn("activity_my_state", field_names)
