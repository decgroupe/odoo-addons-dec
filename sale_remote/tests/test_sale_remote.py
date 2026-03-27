# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Mar 2026

from odoo.tests.common import TransactionCase


class TestSaleRemote(TransactionCase):
    """Tests for sale_remote module."""

    @classmethod
    def setUpClass(cls):
        """Set up shared test data."""
        super().setUpClass()
        cls.partner = cls.env["res.partner"].create({"name": "Test Customer"})
        uom_unit = cls.env.ref("uom.product_uom_unit")
        cls.product = cls.env["product.product"].create(
            {
                "name": "Test Product",
                "type": "consu",
                "is_storable": False,
                "uom_id": uom_unit.id,
                "uom_po_id": uom_unit.id,
                "list_price": 100.0,
                "standard_price": 60.0,
            }
        )
        cls.sale_order = cls.env["sale.order"].create(
            {
                "partner_id": cls.partner.id,
            }
        )

    def test_01_create_line_basic(self):
        """Verify create_line creates a sale order line and returns its id."""
        uom_unit = self.env.ref("uom.product_uom_unit")
        line_id = self.sale_order.create_line(
            self.product.id, uom_unit.id, product_uom_qty=2.0
        )
        self.assertIsInstance(line_id, int)
        line = self.env["sale.order.line"].browse(line_id)
        self.assertTrue(line.exists())
        self.assertEqual(line.order_id, self.sale_order)
        self.assertEqual(line.product_id, self.product)
        self.assertEqual(line.product_uom_qty, 2.0)

    def test_02_create_line_with_markup(self):
        """Verify create_line applies markup_percent and adjusts price_unit."""
        uom_unit = self.env.ref("uom.product_uom_unit")
        line_id = self.sale_order.create_line(
            self.product.id, uom_unit.id, product_uom_qty=1.0, markup_percent=40
        )
        line = self.env["sale.order.line"].browse(line_id)
        self.assertTrue(line.exists())
        # with cost=60 and markup=40%, price = 60 / (1 - 0.40) = 100
        self.assertAlmostEqual(line.price_unit, 100.0, places=2)
