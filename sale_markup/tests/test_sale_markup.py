# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Feb 2026

from odoo import Command
from odoo.tests.common import TransactionCase


class TestSaleMarkup(TransactionCase):
    def setUp(self):
        super().setUp()
        # enable discount
        self.env["res.config.settings"].create(
            {
                "group_uom": True,
                "group_product_pricelist": True,
                "group_discount_per_so_line": True,
            }
        ).execute()
        # create a lambda product with a cost price of 10 and a sale price of 15
        self.product = self.env["product.product"].create(
            {
                "name": "Test Product",
                "standard_price": 10.0,  # cost price
                "list_price": 15.0,  # sale price
                "uom_id": self.env.ref("uom.product_uom_unit").id,
            }
        )
        # create a sale order with one line for 1 unit of the product with no discount
        self.sale_order = self.env["sale.order"].create(
            {
                "partner_id": self.env.ref("base.res_partner_1").id,
                "order_line": [Command.create({"product_id": self.product.id})],
            }
        )
        self.so_line = self.sale_order.order_line[0]

    def test_01_markup(self):
        self.assertEqual(self.so_line.purchase_price, 10.0)
        self.assertEqual(self.so_line.price_unit, 15.0)
        self.assertAlmostEqual(self.so_line.markup_percent, 33.33, places=1)
        # set markup to 50% -> price unit should be 20.0
        self.so_line.markup_percent = 50.0
        # price unit should have been updated
        self.assertEqual(self.so_line.price_unit, 20.0)
        # markup percent must not have changed
        self.assertAlmostEqual(self.so_line.markup_percent, 50.0, places=1)
        # set discount to 10% -> total should be 18.0
        self.so_line.discount = 10.0
        self.assertEqual(self.so_line.price_subtotal, 18.0)
        # markup percent must have changed since discount has changed
        self.assertAlmostEqual(self.so_line.markup_percent, 44.44, places=1)
        # re-set markup to 50% -> price unit should be 22.22
        self.so_line.markup_percent = 50.0
        self.assertEqual(self.so_line.price_unit, 22.22)
        self.assertAlmostEqual(self.so_line.markup_percent, 50.0, places=1)
        # set markup to 99% -> price unit should be 1,111.11
        self.so_line.markup_percent = 99.0
        self.assertEqual(self.so_line.price_unit, 1111.11)
        self.assertEqual(self.so_line.price_subtotal, 1000.0)
        self.assertAlmostEqual(self.so_line.markup_percent, 99.0, places=1)
        # set markup to 100% -> price unit should be 0.0
        self.so_line.markup_percent = 100.0
        self.assertEqual(self.so_line.price_unit, 0.0)
        self.assertEqual(self.so_line.price_subtotal, 0.0)
        self.assertEqual(self.so_line.markup_percent, 0.0)
        self.assertEqual(self.so_line.margin, -10.0)
        # set a price unit of 100 -> markup percent should be 88.89%
        self.so_line.price_unit = 100.0
        self.assertEqual(self.so_line.price_unit, 100.0)
        self.assertEqual(self.so_line.price_subtotal, 90.0)
        self.assertAlmostEqual(self.so_line.markup_percent, 88.89, places=1)
        # remove discount, price must stay the same and markup percent should be 90%
        self.so_line.discount = 0.0
        self.assertEqual(self.so_line.price_unit, 100.0)
        self.assertEqual(self.so_line.price_subtotal, 100.0)
        self.assertAlmostEqual(self.so_line.markup_percent, 90.0, places=1)
        # change quantity to 2 -> price unit and markup should stay the same
        self.so_line.product_uom_qty = 2.0
        self.assertEqual(self.so_line.price_unit, 100.0)
        self.assertEqual(self.so_line.price_subtotal, 200.0)
        self.assertAlmostEqual(self.so_line.markup_percent, 90.0, places=1)
        # set a discount of 50%
        self.so_line.discount = 50.0
        self.assertEqual(self.so_line.price_unit, 100.0)
        self.assertEqual(self.so_line.price_subtotal, 100.0)
        self.assertAlmostEqual(self.so_line.markup_percent, 80.0, places=1)
