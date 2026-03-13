# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Mar 2026

import logging

from odoo.addons.stock_traceability_mrp.tests.common import TestStockTraceabilityMrpBase

_logger = logging.getLogger(__name__)


class TestStockTraceabilityMrpStage(TestStockTraceabilityMrpBase):
    """Tests for Stock Traceability module."""

    def test_01_production_head_description(self):
        production = self.env["mrp.production"].create(
            {
                "name": "WH/MO/TEST/01/01",
                "product_id": self.manufacturable_product.id,
                "product_uom_id": self.manufacturable_product.uom_id.id,
                "product_qty": 1,
            }
        )
        head, desc = production.get_head_desc()
        self.assertEqual(head, f"🔧{production.name}")
        self.assertEqual(desc, "✨Draft")
        # change state to confirmed
        production.action_confirm()
        head, desc = production.get_head_desc()
        self.assertEqual(head, f"🔧{production.name}")
        self.assertEqual(desc, "🏳️Confirmed")
        # change current stage name and symbol
        stage = production.stage_id
        stage.name = "Test Stage"
        stage.symbol = "🧪"
        head, desc = production.get_head_desc()
        self.assertEqual(head, f"🔧{production.name}")
        self.assertEqual(desc, "🧪Test Stage")
