# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Sep 2023

from odoo.tests.common import TransactionCase


class TestProductPackLine(TransactionCase):
    def setUp(self):
        super().setUp()
        self.ProductPackLine = self.env["product.pack.line"]

    def test_01_field_names(self):
        self.assertIn("product_name", self.ProductPackLine._fields)
        self.assertIn("product_code", self.ProductPackLine._fields)
        self.assertIn("product_uom_id", self.ProductPackLine._fields)
        self.assertIn("product_categ_id", self.ProductPackLine._fields)
