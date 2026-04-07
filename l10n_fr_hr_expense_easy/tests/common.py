# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Apr 2026

from odoo.tests.common import TransactionCase


class TestL10nFrHrExpenseEasyCommon(TransactionCase):
    """Base class for l10n_fr_hr_expense_easy tests."""

    @classmethod
    def setUpClass(cls):
        """Set up shared test data for French expense account assignment tests."""
        super().setUpClass()
        cls.Account = cls.env["account.account"]
        cls.ProductProduct = cls.env["product.product"]
        cls.ProductCategory = cls.env["product.category"]
