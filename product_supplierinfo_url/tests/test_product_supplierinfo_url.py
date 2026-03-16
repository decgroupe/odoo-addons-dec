# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Sep 2023

from odoo.tests.common import TransactionCase


class TestProductSupplierinfoUrl(TransactionCase):
    """Test product_supplierinfo_url module."""

    def setUp(self):
        super().setUp()
        self.supplierinfo_model = self.env["product.supplierinfo"]

    def test_01_field_names(self):
        self.assertIn("url", self.supplierinfo_model._fields)
