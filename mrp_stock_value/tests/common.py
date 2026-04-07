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


class TestMrpStockValueCommon(TransactionCase):
    """Common test fixtures for mrp_stock_value tests."""

    @classmethod
    def setUpClass(cls):
        """Set up shared test data."""
        super().setUpClass()
        cls.stock_location = cls.env.ref("stock.stock_location_stock")
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
                "product_id": cls.product_finished.id,
                "product_tmpl_id": cls.product_finished.product_tmpl_id.id,
                "product_qty": 1.0,
                "type": "normal",
                "consumption": "flexible",
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
        cls.env["stock.quant"]._update_available_quantity(
            cls.product_component,
            cls.stock_location,
            100.0,
        )

    def _create_and_complete_mo(self):
        """Create, confirm, and complete a manufacturing order."""
        mo = self.env["mrp.production"].create(
            {
                "product_id": self.product_finished.id,
                "bom_id": self.bom.id,
                "product_qty": 1.0,
            }
        )
        mo.action_confirm()
        mo.qty_producing = mo.product_qty
        mo.move_raw_ids.picked = True
        mo.button_mark_done()
        return mo
