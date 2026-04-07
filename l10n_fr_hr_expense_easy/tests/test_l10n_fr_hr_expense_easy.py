# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Apr 2026

import logging

from odoo.addons.l10n_fr_hr_expense_easy.hooks import (
    assign_category_account,
    assign_product_account,
    get_account,
    post_init_hook,
)

from .common import TestL10nFrHrExpenseEasyCommon

_logger = logging.getLogger(__name__)


class TestL10nFrHrExpenseEasy(TestL10nFrHrExpenseEasyCommon):
    """Tests for l10n_fr_hr_expense_easy module."""

    @classmethod
    def setUpClass(cls):
        """Set up shared test data including test accounts and taxes."""
        super().setUpClass()
        # reuse existing account with code 625100 or create a test one
        cls.account_625100 = cls.Account.search([("code", "=", "625100")], limit=1)
        if not cls.account_625100:
            cls.account_625100 = cls.Account.create(
                {
                    "name": "Test Travel Expenses",
                    "code": "625100",
                    "account_type": "expense",
                }
            )
        # create a test purchase tax for supplier tax assignment tests
        cls.test_tax = cls.env["account.tax"].create(
            {
                "name": "Test Tax 20%",
                "amount": 20.0,
                "amount_type": "percent",
                "type_tax_use": "purchase",
            }
        )

    def test_01_get_account_found(self):
        """get_account returns the account when the code exists."""
        result = get_account(self.env, "625100")
        self.assertTrue(result)
        self.assertEqual(result.code, "625100")

    def test_02_get_account_not_found(self):
        """get_account returns empty recordset and logs warning when code is missing."""
        with self.assertLogs(
            "odoo.addons.l10n_fr_hr_expense_easy.hooks", level=logging.WARNING
        ) as log_cm:
            result = get_account(self.env, "000000")
        self.assertFalse(result)
        self.assertTrue(
            any("000000" in msg for msg in log_cm.output),
            "Expected a warning containing the missing account code",
        )

    def test_03_assign_category_account(self):
        """assign_category_account sets property_account_expense_categ_id on
        category."""
        assign_category_account(self.env, "transport", "625100")
        category = self.env.ref("hr_expense_easy.cat_transport")
        self.assertEqual(
            category.property_account_expense_categ_id,
            self.account_625100,
        )

    def test_04_assign_product_account_without_tax(self):
        """assign_product_account sets account on product without tax."""
        assign_product_account(self.env, "plane", "625100")
        product = self.env.ref("hr_expense_easy.product_product_expense_plane")
        self.assertEqual(
            product.property_account_expense_id,
            self.account_625100,
        )
        self.assertTrue(product.purchase_ok)

    def test_05_assign_product_account_with_tax(self):
        """assign_product_account sets account and supplier tax on product."""
        assign_product_account(self.env, "car_rent", "625100", self.test_tax)
        product = self.env.ref("hr_expense_easy.product_product_expense_car_rent")
        self.assertEqual(
            product.property_account_expense_id,
            self.account_625100,
        )
        self.assertTrue(product.purchase_ok)
        self.assertIn(self.test_tax, product.supplier_taxes_id)

    def test_06_post_init_hook_runs_without_error(self):
        """post_init_hook runs without error even when French COA is not installed."""
        # when French COA taxes are absent, env.ref returns False and the hook
        # gracefully skips tax assignment while still assigning accounts
        post_init_hook(self.env)
        product_transport = self.env.ref(
            "hr_expense_easy.product_product_expense_plane"
        )
        # the hook assigns account 625100 to plane — verify it is set
        account_625100 = self.Account.search([("code", "=", "625100")], limit=1)
        if account_625100:
            self.assertEqual(
                product_transport.property_account_expense_id,
                account_625100,
            )
