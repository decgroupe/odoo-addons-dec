# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Jan 2026

from odoo.tests.common import TransactionCase


class TestPurchaseTypefast(TransactionCase):
    """Test Purchase Typefast Module"""

    def test_01_purchase_name(self):
        partner = self.env["res.partner"].create({"name": "Test Partner"})
        purchase = self.env["purchase.order"].create(
            {
                "name": "⌛ Purchase Order",
                "partner_id": partner.id,
            }
        )
        self.assertEqual(purchase.typefast_name, "PurchaseOrder")
