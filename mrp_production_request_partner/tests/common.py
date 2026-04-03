# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Apr 2026

from odoo.tests.common import TransactionCase


class TestMrpProductionRequestPartnerCommon(TransactionCase):
    """Common test base for mrp_production_request_partner module."""

    @classmethod
    def setUpClass(cls):
        """Set up shared test data."""
        super().setUpClass()
        cls.RequestModel = cls.env["mrp.production.request"]
        cls.WizModel = cls.env["mrp.production.request.create.mo"]
        # [FURN_7800] Desk Combination - has a BOM available in demo data
        cls.product = cls.env.ref("product.product_product_3")
        cls.product.write({"mrp_production_request": True})
        cls.bom = cls.product.bom_ids[:1]
        # use a partner available in demo data as the shipping partner
        cls.partner = cls.env.ref("base.res_partner_1")
