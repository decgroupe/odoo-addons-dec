# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Apr 2026

from odoo import Command
from odoo.tests.common import TransactionCase


class TestPartnerSaleDatesCommon(TransactionCase):
    """Base class with shared fixtures for partner_sale_dates tests."""

    @classmethod
    def setUpClass(cls):
        """Set up shared test data."""
        super().setUpClass()
        cls.partner = cls.env["res.partner"].create(
            {
                "name": "Test Partner",
                "customer_rank": 1,
            }
        )
        cls.product = cls.env["product.product"].create(
            {
                "name": "Test Product",
                "type": "consu",
                "is_storable": False,
            }
        )
        cls.pricelist = cls.env["product.pricelist"].search(
            [("currency_id.name", "=", "EUR")], limit=1
        )

    def _make_sale_order(self, partner=None, state=None):
        """Create a sale order for the given partner and optional state."""
        partner = partner or self.partner
        so = self.env["sale.order"].create(
            {
                "partner_id": partner.id,
                "partner_shipping_id": partner.id,
                "order_line": [
                    Command.create(
                        {
                            "product_id": self.product.id,
                            "product_uom_qty": 1,
                            "price_unit": 10.0,
                        }
                    )
                ],
            }
        )
        if state == "sale":
            so.action_confirm()
        elif state == "cancel":
            so.action_cancel()
        return so
