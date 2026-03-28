# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Mar 2026

from odoo.tests.common import TransactionCase


class TestMrpProductManufacturable(TransactionCase):
    """Tests for mrp_product_manufacturable module."""

    @classmethod
    def setUpClass(cls):
        """Set up shared test data."""
        super().setUpClass()
        cls.Product = cls.env["product.product"]
        cls.Bom = cls.env["mrp.bom"]
        cls.product = cls.Product.create(
            {
                "name": "Test Product",
                "type": "consu",
                "is_storable": True,
            }
        )
        cls.component = cls.Product.create(
            {
                "name": "Test Component",
                "type": "consu",
                "is_storable": True,
            }
        )

    def test_01_no_bom_not_manufacturable(self):
        """A product with no BOM must not be manufacturable."""
        self.assertFalse(self.product.manufacturable)

    def test_02_normal_bom_is_manufacturable(self):
        """A product with an active normal BOM must be manufacturable."""
        bom = self.Bom.create(
            {
                "product_tmpl_id": self.product.product_tmpl_id.id,
                "type": "normal",
            }
        )
        self.product.invalidate_recordset()
        self.assertTrue(self.product.manufacturable)
        bom.unlink()

    def test_03_phantom_bom_not_manufacturable(self):
        """A product with only a phantom BOM must not be manufacturable."""
        bom = self.Bom.create(
            {
                "product_tmpl_id": self.product.product_tmpl_id.id,
                "type": "phantom",
            }
        )
        self.product.invalidate_recordset()
        self.assertFalse(self.product.manufacturable)
        bom.unlink()

    def test_04_archived_bom_not_manufacturable(self):
        """A product with only an archived normal BOM must not be manufacturable."""
        bom = self.Bom.create(
            {
                "product_tmpl_id": self.product.product_tmpl_id.id,
                "type": "normal",
                "active": False,
            }
        )
        self.product.invalidate_recordset()
        self.assertFalse(self.product.manufacturable)
        bom.unlink()

    def test_05_mixed_boms_manufacturable(self):
        """A product with one normal BOM and one phantom BOM must be manufacturable."""
        bom_normal = self.Bom.create(
            {
                "product_tmpl_id": self.product.product_tmpl_id.id,
                "type": "normal",
            }
        )
        bom_phantom = self.Bom.create(
            {
                "product_tmpl_id": self.product.product_tmpl_id.id,
                "type": "phantom",
            }
        )
        self.product.invalidate_recordset()
        self.assertTrue(self.product.manufacturable)
        bom_normal.unlink()
        bom_phantom.unlink()
