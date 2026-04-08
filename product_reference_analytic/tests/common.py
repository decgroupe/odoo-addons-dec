# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Apr 2026

from odoo.tests.common import TransactionCase


class TestProductReferenceAnalyticCommon(TransactionCase):
    """Base class for product_reference_analytic tests."""

    @classmethod
    def setUpClass(cls):
        """Set up shared test data."""
        super().setUpClass()
        cls.company = cls.env.company
        cls.analytic_plan = cls.env.ref(
            "product_reference_analytic.product_analytic_group"
        )
        cls.company.auto_create_reference_category_analytic_account = True
