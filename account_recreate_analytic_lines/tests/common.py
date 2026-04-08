# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Apr 2026

from odoo.tests.common import TransactionCase


class TestRecreateAnalyticLinesCommon(TransactionCase):
    """Common base class with shared fixtures for account_recreate_analytic_lines
    tests."""

    @classmethod
    def setUpClass(cls):
        """Set up shared test data."""
        super().setUpClass()
        cls.partner = cls.env.ref("base.res_partner_12")
        cls.plan = cls.env["account.analytic.plan"].create({"name": "Test Plan ARAL"})
        cls.analytic_account = cls.env["account.analytic.account"].create(
            {
                "name": "Test Income Analytic",
                "plan_id": cls.plan.id,
                "company_id": False,
            }
        )
        cls.product = cls.env["product.product"].create(
            {
                "name": "Test Product ARAL",
                "type": "consu",
            }
        )
        cls.product.product_tmpl_id.income_analytic_account_id = cls.analytic_account
        cls.invoice = cls.env["account.move"].create(
            {
                "partner_id": cls.partner.id,
                "move_type": "out_invoice",
                "invoice_line_ids": [
                    (
                        0,
                        0,
                        {
                            "name": "Test Line",
                            "product_id": cls.product.id,
                            "quantity": 1,
                            "price_unit": 100.0,
                        },
                    )
                ],
            }
        )
