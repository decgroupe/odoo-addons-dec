# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Mar 2026

from odoo import Command, fields
from odoo.tests.common import TransactionCase


class TestProductSupplierinfoUrlPurchase(TransactionCase):
    """Tests for product supplier URL on purchase order line."""

    def setUp(self):
        """prepare common records for product supplier URL tests."""
        super().setUp()
        self.vendor = self.env["res.partner"].create(
            {
                "name": "Vendor A",
                "supplier_rank": 1,
            }
        )
        self.other_vendor = self.env["res.partner"].create(
            {
                "name": "Vendor B",
                "supplier_rank": 1,
            }
        )
        self.product = self.env["product.product"].create(
            {
                "name": "Test Product",
                "type": "consu",
                "purchase_ok": True,
            }
        )
        self.env["product.supplierinfo"].create(
            {
                "partner_id": self.vendor.id,
                "product_tmpl_id": self.product.product_tmpl_id.id,
                "price": 50.0,
                "min_qty": 1.0,
                "url": "https://vendor-a.example.com/min-1",
            }
        )
        self.env["product.supplierinfo"].create(
            {
                "partner_id": self.vendor.id,
                "product_tmpl_id": self.product.product_tmpl_id.id,
                "price": 45.0,
                "min_qty": 10.0,
                "url": "https://vendor-a.example.com/min-10",
            }
        )
        self.env["product.supplierinfo"].create(
            {
                "partner_id": self.other_vendor.id,
                "product_tmpl_id": self.product.product_tmpl_id.id,
                "price": 40.0,
                "min_qty": 1.0,
                "url": "https://vendor-b.example.com/min-1",
            }
        )

    def _create_order_line(self, partner, qty):
        """Create a purchase order with one line and return this line."""
        order = self.env["purchase.order"].create(
            {
                "partner_id": partner.id,
                "order_line": [
                    Command.create(
                        {
                            "product_id": self.product.id,
                            "name": self.product.display_name,
                            "product_qty": qty,
                            "product_uom": self.product.uom_po_id.id,
                            "price_unit": 1.0,
                            "date_planned": fields.Datetime.now(),
                        }
                    )
                ],
            }
        )
        return order.order_line

    def test_01_compute_url_with_selected_vendor_and_quantity(self):
        """compute the URL from the seller selected by partner and quantity."""
        line = self._create_order_line(self.vendor, 10.0)
        self.assertEqual(
            line.product_supplier_url, "https://vendor-a.example.com/min-10"
        )
        line.product_qty = 5.0
        self.assertEqual(
            line.product_supplier_url, "https://vendor-a.example.com/min-1"
        )

    def test_02_compute_url_without_matching_seller(self):
        """keep URL empty when no supplier matches the purchase partner."""
        unknown_vendor = self.env["res.partner"].create(
            {
                "name": "Vendor C",
                "supplier_rank": 1,
            }
        )
        line = self._create_order_line(unknown_vendor, 10.0)
        self.assertFalse(line.product_supplier_url)
