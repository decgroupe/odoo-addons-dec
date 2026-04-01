# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Sep 2023

from lxml import etree

from odoo.tests.common import TransactionCase


class TestSalePurchaseTraceability(TransactionCase):
    """Tests for sale_purchase_traceability module."""

    @classmethod
    def setUpClass(cls):
        """Set up shared test data."""
        super().setUpClass()

    def test_01_form_view_fields(self):
        """Check that purchase_line_ids is present in the combined sale order
        form view arch."""
        view_info = self.env["sale.order"].get_view(view_type="form")
        arch = etree.fromstring(view_info["arch"])
        field_names = [el.get("name") for el in arch.iter("field")]
        self.assertIn("purchase_line_ids", field_names)

    def test_02_purchases_div_invisible_modifier(self):
        """Check that the purchases div has the correct invisible modifier."""
        view_info = self.env["sale.order"].get_view(view_type="form")
        arch = etree.fromstring(view_info["arch"])
        purchases_div = arch.find(".//*[@name='purchases']")
        self.assertIsNotNone(purchases_div)
        invisible = purchases_div.get("invisible")
        self.assertEqual(invisible, "display_type or not purchase_line_ids")

    def test_03_security_group_exists(self):
        """Check that the sale_purchase_traceability security group exists."""
        group = self.env.ref(
            "sale_purchase_traceability.group_sale_purchase_traceability"
        )
        self.assertTrue(group)
