# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Jan 2026

from odoo.tests.common import TransactionCase


class TestMrpTypefast(TransactionCase):
    """Test MRP Typefast Module"""

    def test_01_production_name(self):
        product = self.env["product.product"].create({"name": "Test Product"})
        production = self.env["mrp.production"].create(
            {
                "name": "⚙️/MO/123/Production Order",
                "product_id": product.id,
                "product_qty": 1.0,
                "product_uom_id": product.uom_id.id,
            }
        )
        self.assertEqual(production.typefast_name, "MO123ProductionOrder")
