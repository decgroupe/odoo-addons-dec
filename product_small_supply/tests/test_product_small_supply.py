# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Nov 2023

from odoo.tests.common import TransactionCase


class TestProductSmallSupply(TransactionCase):
    """ """

    def setUp(self):
        super().setUp()
        self.product27 = self.env.ref("product.product_product_27_product_template")
        self.consumable = self.env["product.product"].create({
            "name": "MyConsumable",
            "type": "consu",
        })

    def test_01_product_is_consumable(self):
        self.assertFalse(self.product27.is_consumable)
        self.assertEqual(self.product27.type, "product")
        self.product27.small_supply = True
        self.assertTrue(self.product27.is_consumable)
        self.assertEqual(self.product27.type, "product")

    def test_02_service_is_not_consumable(self):
        self.assertEqual(self.consumable.type, "consu")
        self.assertTrue(self.consumable.is_consumable)
        self.consumable.type = "service"
        self.assertFalse(self.consumable.is_consumable)
        self.assertFalse(self.consumable.small_supply)

    def test_03_small_supply_is_consumable(self):
        self.assertEqual(self.consumable.type, "consu")
        self.assertTrue(self.consumable.is_consumable)
        self.consumable.type = "product"
        self.assertFalse(self.consumable.is_consumable)
        self.consumable.small_supply = True
        self.assertTrue(self.consumable.is_consumable)
        self.consumable.type = "consu"
        self.assertTrue(self.consumable.is_consumable)
        self.assertFalse(self.consumable.small_supply)