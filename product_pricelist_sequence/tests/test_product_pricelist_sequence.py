# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Jan 2026

from odoo import Command
from odoo.tests.common import TransactionCase


class TestProductPricelistSequence(TransactionCase):
    def setUp(self):
        super().setUp()
        self.pricelist_model = self.env["product.pricelist"]
        self.pricelist_item_model = self.env["product.pricelist.item"]

    def test_01_naming(self):
        pricelist_id = self.pricelist_model.create(
            {
                "name": "Pricelist 01",
                "item_ids": [
                    Command.create(
                        {
                            "applied_on": "3_global",
                            "compute_price": "formula",
                            "base": "list_price",
                            "note": "First item",
                        }
                    )
                ],
            }
        )
        item = pricelist_id.item_ids[0]
        self.assertEqual(item.name, "First item 🢒 All Products")
        item.note = False
        self.assertEqual(item.name, "All Products")

    def test_02_sequence(self):
        product_id = self.env["product.product"].create(
            {
                "name": "Product 02",
                "uom_id": self.env.ref("uom.product_uom_unit").id,
                "lst_price": 100,
                "standard_price": 80,
            }
        )
        pricelist = self.pricelist_model.create(
            {
                "name": "Pricelist 02",
                "item_ids": [
                    Command.create(
                        {
                            "sequence": 10,
                            "applied_on": "1_product",
                            "compute_price": "fixed",
                            "fixed_price": 100,
                            "product_id": product_id.id,
                        }
                    ),
                    Command.create(
                        {
                            "sequence": 5,
                            "applied_on": "1_product",
                            "compute_price": "fixed",
                            "fixed_price": 120,
                            "product_id": product_id.id,
                        }
                    ),
                    Command.create(
                        {
                            "sequence": 20,
                            "applied_on": "1_product",
                            "compute_price": "fixed",
                            "fixed_price": 140,
                            "product_id": product_id.id,
                        }
                    ),
                ],
            }
        )
        domain = [("pricelist_id", "=", pricelist.id)]
        rules = self.pricelist_item_model.search(domain)
        for rule, sequence, price in [
            (rules[0], 5, 120),
            (rules[1], 10, 100),
            (rules[2], 20, 140),
        ]:
            self.assertEqual(rule.sequence, sequence)
            self.assertEqual(rule.fixed_price, price)
        # the lower sequence has the priority
        price = pricelist._get_product_price(product_id, 1)
        self.assertEqual(price, 120)
        # create a new rule "global" with a greater sequence (global rules have less
        # priority in Odoo, but a lower sequence should have more priority)
        self.pricelist_item_model.create(
            {
                "sequence": 3,
                "applied_on": "3_global",
                "compute_price": "fixed",
                "fixed_price": 90,
                "pricelist_id": pricelist.id,
            }
        )
        price = pricelist._get_product_price(product_id, 1)
        self.assertEqual(price, 90)
        # print([(r.sequence, r.fixed_price) for r in rules])
