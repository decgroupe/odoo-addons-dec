# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Feb 2026

from odoo import Command
from odoo.tests.common import TransactionCase


class TestMrpBomPrices(TransactionCase):
    """Test the computation of cost price, unit price and public price on BoM lines."""

    def setUp(self):
        super().setUp()

        # create products (components and main product)
        self.comp1 = self.env["product.product"].create(
            {"name": "Component 1", "standard_price": 10.0, "lst_price": 15.0}
        )
        self.comp2 = self.env["product.product"].create(
            {"name": "Component 2", "standard_price": 20.0, "lst_price": 25.0}
        )
        self.comp3 = self.env["product.product"].create(
            {"name": "Component 3", "standard_price": 30.0, "lst_price": 35.0}
        )
        self.main_product = self.env["product.product"].create(
            {"name": "Main Product", "standard_price": 0.0, "lst_price": 0.0}
        )
        # BoM for main product
        self.bom = self.env["mrp.bom"].create(
            {
                "product_id": self.main_product.id,
                "product_tmpl_id": self.main_product.product_tmpl_id.id,
                "bom_line_ids": [
                    Command.create({"product_id": self.comp1.id, "product_qty": 2}),
                    Command.create({"product_id": self.comp2.id, "product_qty": 3}),
                    Command.create({"product_id": self.comp3.id, "product_qty": 1}),
                ],
            }
        )

    def test_01_prices(self):
        # get BoM lines
        l1, l2, l3 = self.bom.bom_line_ids
        # check prices
        self.assertEqual(l1.unit_price, 10.0)
        self.assertEqual(l1.public_price, 15.0)
        self.assertEqual(l1.cost_price, 20.0)
        self.assertEqual(l2.unit_price, 20.0)
        self.assertEqual(l2.public_price, 25.0)
        self.assertEqual(l2.cost_price, 60.0)
        self.assertEqual(l3.unit_price, 30.0)
        self.assertEqual(l3.public_price, 35.0)
        self.assertEqual(l3.cost_price, 30.0)
        # total price
        self.assertEqual(self.bom.cost_price, 110.0)
        # create supplier info for comp1 with different price
        seller1 = self.env["res.partner"].create({"name": "Supplier #1"})
        self.env["product.supplierinfo"].create(
            {
                "partner_id": seller1.id,
                "product_id": self.comp1.id,
                "min_qty": 1,
                "price": 9.0,
            }
        )
        l1.invalidate_recordset()
        self.assertEqual(l1.unit_price, 9.0)
        # create a second supplier
        seller2 = self.env["res.partner"].create({"name": "Supplier #2"})
        self.env["product.supplierinfo"].create(
            {
                "partner_id": seller2.id,
                "product_id": self.comp1.id,
                "min_qty": 2,
                "price": 8.0,
            }
        )
        l1.invalidate_recordset()
        self.assertEqual(l1.unit_price, 8.0)
        # force supplier selection by setting partner on BoM line
        l1.partner_id = seller1
        self.assertEqual(l1.unit_price, 9.0)
