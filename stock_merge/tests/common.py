# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, May 2026

from odoo.tests.common import TransactionCase


class TestStockMergeCommon(TransactionCase):
    """Shared fixtures for stock_merge tests."""

    @classmethod
    def setUpClass(cls):
        """Set up shared models for tests."""
        super().setUpClass()
        cls.merge_stock_move_wizard_model = cls.env["merge.stock.move.wizard"]

    def _create_wizard(self):
        """Create a stock move merge wizard record."""
        return self.merge_stock_move_wizard_model.create({})
