# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Apr 2026

from odoo.tests.common import TransactionCase


class TestSaleDeliveryRateCommon(TransactionCase):
    """Base class with shared fixtures for sale_delivery_rate tests."""

    @classmethod
    def setUpClass(cls):
        """Set up shared test data."""
        super().setUpClass()
        cls.partner = cls.env["res.partner"].create({"name": "Test Partner"})
        cls.uom_unit = cls.env.ref("uom.product_uom_unit")
        # storable product (consu + is_storable) to trigger delivery
        cls.storable_product = cls.env["product.product"].create(
            {
                "name": "Storable Product",
                "type": "consu",
                "is_storable": True,
            }
        )
        # service product — does not go through delivery
        cls.service_product = cls.env["product.product"].create(
            {
                "name": "Service Product",
                "type": "service",
            }
        )
