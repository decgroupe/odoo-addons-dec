# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Sep 2023

from odoo.tests import Form
from odoo.tests.common import TransactionCase


class TestProductLocation(TransactionCase):
    def setUp(self):
        super().setUp()
        self.ProductTemplate = self.env["product.template"]

    def test_01_location_fields(self):
        product = self.ProductTemplate.create(
            {
                "name": "Test Product",
                "loc_rack": "Rack 1",
                "loc_row": "Row 2",
                "loc_case": "Case 3",
            }
        )
        self.assertEqual(product.loc_rack, "Rack 1")
        self.assertEqual(product.loc_row, "Row 2")
        self.assertEqual(product.loc_case, "Case 3")

        # Test search
        domain = [
            ("loc_rack", "=", "Rack 1"),
            ("loc_row", "=", "Row 2"),
            ("loc_case", "=", "Case 3"),
        ]
        found_product = self.ProductTemplate.search(domain)
        self.assertIn(product, found_product)

    def test_02_location_fields(self):
        product = self.ProductTemplate.create(
            {
                "name": "Test Service Product",
                "type": "service",
            }
        )
        # add system user to 'Stock Packaging' group to ensure fields are loaded
        # in form view but not editable
        self.env.user.groups_id += self.env.ref("product.group_stock_packaging")
        with Form(product) as product_form:
            with self.assertRaises(AssertionError):
                product_form.loc_rack = "Rack A"
            with self.assertRaises(AssertionError):
                product_form.loc_row = "Row B"
            with self.assertRaises(AssertionError):
                product_form.loc_case = "Case C"
