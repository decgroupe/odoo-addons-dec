# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Apr 2026

from lxml import etree

from .common import TestProcurementTraceabilitySaleCommon


class TestProcurementTraceabilitySale(TestProcurementTraceabilitySaleCommon):
    """Tests for procurement_traceability_sale module."""

    def test_01_sale_order_count(self):
        """sale_order_count on a procurement group reflects linked sale orders."""
        self.group.invalidate_recordset()
        self.assertEqual(self.group.sale_order_count, 1)

    def test_02_sale_order_ids(self):
        """sale_order_ids returns the sale orders linked to the procurement group."""
        self.group.invalidate_recordset()
        self.assertIn(self.sale_order, self.group.sale_order_ids)

    def test_03_sale_order_count_multiple(self):
        """sale_order_count increments when additional sale orders are linked."""
        self.SaleOrder.create(
            {
                "partner_id": self.partner.id,
                "procurement_group_id": self.group.id,
            }
        )
        self.group.invalidate_recordset()
        self.assertEqual(self.group.sale_order_count, 2)

    def test_04_action_view_sale_orders(self):
        """action_view_sale_orders returns an action filtered to the group's orders."""
        action = self.group.action_view_sale_orders()
        self.assertIsInstance(action, dict)
        self.assertIn("domain", action)
        self.assertIn(("procurement_group_id", "=", self.group.id), action["domain"])

    def test_05_procurement_group_form_view_fields(self):
        """Expected fields are present in the combined procurement group form arch."""
        view = self.env.ref("procurement_traceability_sale.procurement_group_form_view")
        view_info = self.env["procurement.group"].get_view(
            view_id=view.id, view_type="form"
        )
        arch = etree.fromstring(view_info["arch"].encode())
        field_names = [el.get("name") for el in arch.iter("field")]
        self.assertIn("sale_order_count", field_names)
        self.assertIn("sale_order_ids", field_names)
        self.assertIn("sale_id", field_names)

    def test_06_procurement_group_list_view_fields(self):
        """Expected fields are present in the combined procurement group list arch."""
        view = self.env.ref("procurement_traceability_sale.procurement_group_tree_view")
        view_info = self.env["procurement.group"].get_view(
            view_id=view.id, view_type="list"
        )
        arch = etree.fromstring(view_info["arch"].encode())
        field_names = [el.get("name") for el in arch.iter("field")]
        self.assertIn("sale_id", field_names)

    def test_07_sale_order_form_view_has_procurement_group(self):
        """procurement_group_id field is present in the sale order form arch."""
        view_info = self.env["sale.order"].get_view(view_type="form")
        arch = etree.fromstring(view_info["arch"].encode())
        field_names = [el.get("name") for el in arch.iter("field")]
        self.assertIn("procurement_group_id", field_names)
