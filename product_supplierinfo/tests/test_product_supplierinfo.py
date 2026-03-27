# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Sep 2023

from odoo.tests.common import TransactionCase


class TestProductSupplierinfo(TransactionCase):
    """Tests for product_supplierinfo module."""

    @classmethod
    def setUpClass(cls):
        """Set up shared test data."""
        super().setUpClass()

    def setUp(self):
        super().setUp()

    def test_01_search_view_fields(self):
        """Verify that the inherited search view contains the expected fields."""
        view = self.env.ref("product_supplierinfo.product_supplierinfo_form_view")
        self.assertTrue(view)
        arch = view.get_combined_arch()
        self.assertIn("×", arch)
