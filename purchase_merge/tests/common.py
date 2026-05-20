# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, May 2026

from odoo.tests.common import TransactionCase


class TestPurchaseMergeCommon(TransactionCase):
    """Base class for purchase_merge tests."""

    @classmethod
    def setUpClass(cls):
        """Set up shared test data from demo records."""
        super().setUpClass()
        cls.purchase_model = cls.env["purchase.order"]
        cls.purchase_line_model = cls.env["purchase.order.line"]
        cls.procurement_group_model = cls.env["procurement.group"]
        cls.merge_order_wizard_model = cls.env["purchase.order.merge"]
        cls.order_1 = cls.env.ref("purchase_merge.purchase_order_1")
        cls.order_2 = cls.env.ref("purchase_merge.purchase_order_2")
        cls.order_3 = cls.env.ref("purchase_merge.purchase_order_3")
