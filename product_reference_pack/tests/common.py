# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Apr 2026

from odoo.tests.common import TransactionCase


class TestProductReferencePackCommon(TransactionCase):
    """Common base class with shared fixtures for product_reference_pack tests."""

    @classmethod
    def setUpClass(cls):
        """Set up shared test data."""
        super().setUpClass()
        cls.ProductTemplate = cls.env["product.template"]
        cls.ProductProduct = cls.env["product.product"]
        cls.RefPack = cls.env["ref.pack"]
        # product that can be sold and purchased
        cls.product_both = cls.ProductTemplate.create(
            {
                "name": "Test Pack Both",
                "type": "consu",
                "sale_ok": True,
                "purchase_ok": True,
            }
        )
        # product that can only be sold
        cls.product_sale = cls.ProductTemplate.create(
            {
                "name": "Test Pack Sale Only",
                "type": "consu",
                "sale_ok": True,
                "purchase_ok": False,
            }
        )
        # product that can only be purchased
        cls.product_purchase = cls.ProductTemplate.create(
            {
                "name": "Test Pack Purchase Only",
                "type": "consu",
                "sale_ok": False,
                "purchase_ok": True,
            }
        )
