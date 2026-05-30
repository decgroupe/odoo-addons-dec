# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, May 2026

from odoo.tests.common import TransactionCase


class TestSaleActivityMyCommon(TransactionCase):
    """Common fixtures for sale_activity_my tests."""

    @classmethod
    def setUpClass(cls):
        """Set up model and inherited views used by the tests."""
        super().setUpClass()
        cls.SaleOrder = cls.env["sale.order"]
        cls.quotation_tree_view = cls.env.ref("sale.view_quotation_tree")
        cls.order_tree_view = cls.env.ref("sale.view_order_tree")
        cls.order_kanban_view = cls.env.ref("sale.view_sale_order_kanban")
