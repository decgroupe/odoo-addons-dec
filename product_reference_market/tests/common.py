# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Apr 2026

from odoo.tests.common import TransactionCase


class TestProductReferenceMarketCommon(TransactionCase):
    """Common base class with shared fixtures for product_reference_market tests."""

    @classmethod
    def setUpClass(cls):
        """Set up shared test data."""
        super().setUpClass()
        # create a basic product for use in market BoMs
        cls.product = cls.env["product.product"].create(
            {
                "name": "Test Product",
                "type": "consu",
            }
        )
        # create a service product used as labor
        cls.labor_service = cls.env["product.product"].create(
            {
                "name": "Labor Service",
                "type": "service",
            }
        )
        # retrieve standard UoMs
        cls.uom_hour = cls.env.ref("uom.product_uom_hour")
        cls.uom_day = cls.env.ref("uom.product_uom_day")
        cls.uom_unit = cls.env.ref("uom.product_uom_unit")
        # create a market BoM for the test product
        cls.market_bom = cls.env["ref.market.bom"].create(
            {
                "product_id": cls.product.id,
                "markup_rate": 10.0,
                "material_cost_factor": 1.5,
            }
        )
