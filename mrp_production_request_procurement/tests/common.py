# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Apr 2026

from odoo import Command
from odoo.tests.common import TransactionCase


class TestMrpProductionRequestProcurementCommon(TransactionCase):
    """Base class with shared fixtures for mrp_production_request_procurement tests."""

    @classmethod
    def setUpClass(cls):
        """Set up shared test data."""
        super().setUpClass()
        cls.request_model = cls.env["mrp.production.request"]
        cls.wizard_model = cls.env["mrp.production.request.create.mo"]
        # find the manufacturing picking type for the current company
        cls.picking_type_manuf = cls.env["stock.picking.type"].search(
            [
                ("code", "=", "mrp_operation"),
                ("company_id", "=", cls.env.company.id),
            ],
            limit=1,
        )
        # create a storable product
        cls.product = cls.env["product.product"].create(
            {
                "name": "Test MRP Product",
                "type": "consu",
                "is_storable": True,
            }
        )
        # create a component product
        cls.component = cls.env["product.product"].create(
            {
                "name": "Test MRP Component",
                "type": "consu",
                "is_storable": True,
            }
        )
        # create a bill of materials
        cls.bom = cls.env["mrp.bom"].create(
            {
                "product_tmpl_id": cls.product.product_tmpl_id.id,
                "product_id": cls.product.id,
                "product_uom_id": cls.product.uom_id.id,
                "product_qty": 1.0,
                "type": "normal",
                "bom_line_ids": [
                    Command.create(
                        {
                            "product_id": cls.component.id,
                            "product_qty": 1.0,
                        }
                    )
                ],
            }
        )

    def _create_production_request(self, qty=1.0, **kwargs):
        """Create a minimal mrp.production.request for tests."""
        vals = {
            "product_id": self.product.id,
            "bom_id": self.bom.id,
            "product_qty": qty,
            "picking_type_id": self.picking_type_manuf.id,
        }
        vals.update(kwargs)
        return self.request_model.create(vals)

    def _create_wizard(self, request):
        """Create the MO creation wizard for the given request."""
        ctx = {
            "active_ids": request.ids,
            "active_model": request._name,
        }
        return self.wizard_model.with_context(**ctx).create({})
