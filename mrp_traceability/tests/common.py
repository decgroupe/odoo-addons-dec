# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, May 2026

from odoo import Command
from odoo.tests.common import TransactionCase


class TestMrpTraceabilityCommon(TransactionCase):
    """Base class with shared fixtures for mrp_traceability tests."""

    @classmethod
    def setUpClass(cls):
        """Set up products, bill of materials and warehouse reference for all tests."""
        super().setUpClass()
        cls.warehouse = cls.env.ref("stock.warehouse0")
        cls.product_finished = cls.env["product.product"].create(
            {
                "name": "Test Finished Product",
                "type": "consu",
                "is_storable": True,
            }
        )
        cls.product_component = cls.env["product.product"].create(
            {
                "name": "Test Component",
                "type": "consu",
                "is_storable": True,
            }
        )
        cls.bom = cls.env["mrp.bom"].create(
            {
                "product_tmpl_id": cls.product_finished.product_tmpl_id.id,
                "product_qty": 1.0,
                "bom_line_ids": [
                    Command.create(
                        {
                            "product_id": cls.product_component.id,
                            "product_qty": 1.0,
                        }
                    )
                ],
            }
        )

    def _create_production(self, qty=1.0):
        """Create and confirm a production order for the test finished product."""
        production = self.env["mrp.production"].create(
            {
                "product_id": self.product_finished.id,
                "product_qty": qty,
                "bom_id": self.bom.id,
            }
        )
        production.action_confirm()
        return production

    def _create_move_line(self, move):
        """Create a minimal stock.move.line for the given move."""
        return self.env["stock.move.line"].create(
            {
                "move_id": move.id,
                "product_id": move.product_id.id,
                "location_id": move.location_id.id,
                "location_dest_id": move.location_dest_id.id,
                "quantity": 0,
            }
        )
