# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by GitHub Copilot <copilot at github.com>, Mar 2026

from odoo import Command
from odoo.tests import TransactionCase


class TestMrpConsumeBase(TransactionCase):
    """Base class for MRP Consume tests."""

    @classmethod
    def setUpClass(cls):
        """Set up test data."""
        super().setUpClass()
        # Create a simple product
        cls.product = cls.env["product.product"].create(
            {
                "name": "Test Product",
                "type": "consu",
                "is_storable": True,
            }
        )
        # Create raw materials
        cls.raw_material_1 = cls.env["product.product"].create(
            {
                "name": "Raw Material 1",
                "type": "consu",
                "is_storable": True,
            }
        )
        cls.raw_material_2 = cls.env["product.product"].create(
            {
                "name": "Raw Material 2",
                "type": "consu",
                "is_storable": True,
            }
        )
        cls.raw_material_make_to_order = cls.env["product.product"].create(
            {
                "name": "Raw Material Make-to-Order",
                "type": "consu",
                "is_storable": True,
            }
        )
        # Create a warehouse
        cls.warehouse = cls.env["stock.warehouse"].search([], limit=1)
        # Create a BOM
        cls.bom = cls.env["mrp.bom"].create(
            {
                "product_tmpl_id": cls.product.product_tmpl_id.id,
                "product_id": cls.product.id,
                "product_qty": 1,
                "type": "normal",
                "bom_line_ids": [
                    Command.create(
                        {
                            "product_id": cls.raw_material_1.id,
                            "product_qty": 2,
                        }
                    ),
                    Command.create(
                        {
                            "product_id": cls.raw_material_2.id,
                            "product_qty": 1,
                        }
                    ),
                    Command.create(
                        {
                            "product_id": cls.raw_material_make_to_order.id,
                            "product_qty": 1,
                        }
                    ),
                ],
            }
        )
