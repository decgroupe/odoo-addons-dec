# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Apr 2026

from lxml import etree

from odoo import Command
from odoo.tests.common import TransactionCase


class TestSaleAccountTraceability(TransactionCase):
    """Tests for sale_account_traceability module."""

    @classmethod
    def setUpClass(cls):
        """Set up shared test data."""
        super().setUpClass()
        cls.partner = cls.env.ref("base.res_partner_12")
        cls.product = cls.env.ref("product.product_product_5")
        cls.product_order = cls.env["product.product"].create(
            {
                "name": "Test Product (Order Invoice)",
                "type": "consu",
                "invoice_policy": "order",
                "list_price": 100.0,
            }
        )
        cls.SaleOrder = cls.env["sale.order"]
        cls.SaleOrderLine = cls.env["sale.order.line"]

    def _create_sale_order(self, product=None, price_unit=100.0):
        """Create a confirmed sale order with one line."""
        product = product or self.product
        so = self.SaleOrder.create(
            {
                "partner_id": self.partner.id,
                "order_line": [
                    Command.create(
                        {
                            "product_id": product.id,
                            "price_unit": price_unit,
                            "product_uom_qty": 1,
                        }
                    )
                ],
            }
        )
        so.action_confirm()
        return so

    def test_01_action_force_invoiced_toggles(self):
        """action_force_invoiced toggles force_invoiced on the line."""
        so = self._create_sale_order()
        line = so.order_line[0]
        self.assertFalse(line.force_invoiced)
        line.action_force_invoiced()
        self.assertTrue(line.force_invoiced)
        line.action_force_invoiced()
        self.assertFalse(line.force_invoiced)

    def test_02_line_force_invoiced_sets_invoice_status(self):
        """When force_invoiced is set on a line, invoice_status becomes invoiced."""
        so = self._create_sale_order(product=self.product_order)
        line = so.order_line[0]
        self.assertEqual(line.invoice_status, "to invoice")
        line.force_invoiced = True
        line.invalidate_recordset()
        self.assertEqual(line.invoice_status, "invoiced")

    def test_03_draft_state_sets_invoice_status_no(self):
        """In draft state, invoice_status is always 'no'."""
        so = self.SaleOrder.create(
            {
                "partner_id": self.partner.id,
                "order_line": [
                    Command.create(
                        {
                            "product_id": self.product.id,
                            "price_unit": 100.0,
                            "product_uom_qty": 1,
                        }
                    )
                ],
            }
        )
        # the order is still in draft state
        self.assertEqual(so.state, "draft")
        line = so.order_line[0]
        self.assertEqual(line.invoice_status, "no")

    def test_04_order_force_invoiced_zero_price_line(self):
        """When the order force_invoiced is set and the line price is 0,
        invoice_status becomes invoiced."""
        so = self._create_sale_order(price_unit=0.0)
        line = so.order_line[0]
        self.assertEqual(line.price_total, 0.0)
        # set force_invoiced at order level (provided by sale_force_invoiced)
        so.force_invoiced = True
        line.invalidate_recordset()
        self.assertEqual(line.invoice_status, "invoiced")

    def test_05_form_view_fields(self):
        """Check that expected fields are present in the form view arch."""
        view = self.env.ref("sale_account_traceability.sale_order_form_view")
        view_info = self.env["sale.order"].get_view(view_id=view.id, view_type="form")
        arch = etree.fromstring(view_info["arch"])
        field_names = [el.get("name") for el in arch.iter("field")]
        self.assertIn("force_invoiced", field_names)
        self.assertIn("invoice_lines", field_names)
