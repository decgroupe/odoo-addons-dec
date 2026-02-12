# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Sep 2023

from odoo.tests.common import TransactionCase


class TestProductPicking(TransactionCase):
    def setUp(self):
        super().setUp()
        self.ProductTemplate = self.env["product.template"]

    def test_01_field_names(self):
        self.assertIn("picking_uom", self.ProductTemplate._fields)

    def test_02_selection(self):
        product = self.ProductTemplate.create(
            {
                "name": "Test product",
            }
        )
        self.assertEqual(
            product.picking_uom,
            False,
            "Default value of `picking_uom` should be False",
        )
        product.picking_uom = "default_uom"
        self.assertEqual(
            product.picking_uom,
            "default_uom",
            "Value of `picking_uom` should be 'default_uom' after assignment",
        )
        product.picking_uom = "purchase_uom"
        self.assertEqual(
            product.picking_uom,
            "purchase_uom",
            "Value of `picking_uom` should be 'purchase_uom' after assignment",
        )
        product.picking_uom = False
        self.assertEqual(
            product.picking_uom,
            False,
            "Value of `picking_uom` should be unset when assigned False",
        )
