# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Mar 2026

import logging

from odoo.addons.stock_traceability_mrp.tests.common import TestStockTraceabilityMrpBase

_logger = logging.getLogger(__name__)


class TestStockTraceabilityMrpSupplyProgress(TestStockTraceabilityMrpBase):
    """Tests for Stock Traceability module."""

    def _create_component_in_bom(self, name, bom):
        product = self.env["product.product"].create(
            {
                "name": f"Component {name}",
                "type": "consu",
                "is_storable": True,
            }
        )
        self.env["mrp.bom.line"].create(
            {"product_id": product.id, "product_qty": 1, "bom_id": bom.id}
        )
        return product

    def test_01_production_head_description(self):
        self._create_component_in_bom("#2", self.bom)
        self._create_component_in_bom("#3", self.bom)
        self._create_component_in_bom("#4", self.bom)
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
        # change first move to update stage
        move = production.move_raw_ids[0]
        move.quantity = 1
        production._compute_supply_progress()
        self.assertEqual(production.stage_id.code, "supplying")
        head, desc = production.get_head_desc()
        self.assertEqual(head, f"🔧{production.name}")
        self.assertEqual(desc, "🛒Supplying 25%")
        # change stage code, progress should be missing
        production.stage_id.code = "Tututu"
        head, desc = production.get_head_desc()
        self.assertEqual(head, f"🔧{production.name}")
        self.assertEqual(desc, "🛒Supplying")
        production.stage_id.code = "supplying"
        # change move 2 and 3 to update progress
        for move in production.move_raw_ids[1:3]:
            move.quantity = 1
        production._compute_supply_progress()
        self.assertEqual(production.stage_id.code, "supplying")
        head, desc = production.get_head_desc()
        self.assertEqual(head, f"🔧{production.name}")
        self.assertEqual(desc, "🛒Supplying 75%")
        # change all moves to update stage
        for move in production.move_raw_ids:
            move.quantity = 1
        production._compute_supply_progress()
        self.assertEqual(production.supply_progress, 100.0)
        self.assertEqual(production.stage_id.code, "build_ready")
        head, desc = production.get_head_desc()
        self.assertEqual(head, f"🔧{production.name}")
        self.assertEqual(desc, "👍Ready to Build")
