# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Apr 2026

import contextlib
from unittest.mock import Mock

import odoo
from odoo import Command
from odoo.tests.common import TransactionCase
from odoo.tools.misc import DotDict


@contextlib.contextmanager
def MockDebugRequest(env):
    """Simulate a debug HTTP request so base.group_no_one is active."""
    request = Mock(
        db=None,
        env=env,
        session=DotDict(debug=True),
    )
    with contextlib.ExitStack() as s:
        odoo.http._request_stack.push(request)
        s.callback(odoo.http._request_stack.pop)
        yield request


class TestPurchaseOrderStockPickingLinkCommon(TransactionCase):
    """Common base class for purchase_order_stock_picking_link tests."""

    @classmethod
    def setUpClass(cls):
        """Set up shared test data."""
        super().setUpClass()
        cls.partner = cls.env["res.partner"].create({"name": "Test Vendor"})
        cls.product = cls.env["product.product"].create(
            {
                "name": "Test Product",
                "type": "consu",
                "is_storable": True,
            }
        )
        cls.location_stock = cls.env.ref("stock.stock_location_stock")
        cls.location_customers = cls.env.ref("stock.stock_location_customers")
        cls.picking_type_out = cls.env.ref("stock.picking_type_out")

    def _create_purchase_order(self):
        """Create and confirm a purchase order with one line."""
        po = self.env["purchase.order"].create(
            {
                "partner_id": self.partner.id,
                "order_line": [
                    Command.create(
                        {
                            "product_id": self.product.id,
                            "product_qty": 10.0,
                            "product_uom": self.product.uom_po_id.id,
                            "price_unit": 50.0,
                        }
                    )
                ],
            }
        )
        po.button_confirm()
        return po

    def _create_outgoing_picking(self):
        """Create an outgoing (delivery) picking with a stock move."""
        picking = self.env["stock.picking"].create(
            {
                "partner_id": self.partner.id,
                "picking_type_id": self.picking_type_out.id,
                "location_id": self.location_stock.id,
                "location_dest_id": self.location_customers.id,
            }
        )
        move = self.env["stock.move"].create(
            {
                "name": self.product.name,
                "picking_id": picking.id,
                "product_id": self.product.id,
                "product_uom_qty": 10.0,
                "product_uom": self.product.uom_id.id,
                "location_id": self.location_stock.id,
                "location_dest_id": self.location_customers.id,
            }
        )
        return picking, move
