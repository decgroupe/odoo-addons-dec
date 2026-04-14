# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Apr 2026

from odoo.tests.common import TransactionCase


class TestAccountSaleTraceabilityCommon(TransactionCase):
    """Base class for account_sale_traceability tests."""

    @classmethod
    def setUpClass(cls):
        """Set up shared test data."""
        super().setUpClass()
        cls.product = cls.env["product.product"].search([], limit=1)
        cls.partner = cls.env["res.partner"].create({"name": "Test Partner"})
        cls.sale_account = cls.env["account.account"].search(
            [
                (
                    "account_type",
                    "=",
                    "income",
                ),
                ("company_ids", "=", cls.env.company.id),
            ],
            limit=1,
        )
        cls.journal = cls.env["account.journal"].search(
            [("type", "=", "sale"), ("company_id", "=", cls.env.company.id)],
            limit=1,
        )
