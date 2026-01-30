# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Jan 2026

from odoo import Command
from odoo.tests.common import TransactionCase


class TestStockAutoValidate(TransactionCase):
    def setUp(self):
        super().setUp()
        self.warehouse = self.env.ref("stock.warehouse0")
        self.product = self.env["product.product"].create(
            {
                "name": "Test Product",
                "type": "consu",
                "is_storable": True,
            }
        )
        self.picking_type_in = self.warehouse.in_type_id
        self.picking_type_out = self.warehouse.out_type_id

    def _create_pickings(self, auto_validate=False):
        # create incoming picking
        picking_in = self.env["stock.picking"].create(
            {
                "picking_type_id": self.picking_type_in.id,
                "location_id": self.env.ref("stock.stock_location_suppliers").id,
                "location_dest_id": self.warehouse.lot_stock_id.id,
            }
        )
        move_in = self.env["stock.move"].create(
            {
                "name": "Move In",
                "product_id": self.product.id,
                "product_uom_qty": 10,
                "product_uom": self.product.uom_id.id,
                "picking_id": picking_in.id,
                "location_id": picking_in.location_id.id,
                "location_dest_id": picking_in.location_dest_id.id,
            }
        )
        # create outgoing picking
        picking_out = self.env["stock.picking"].create(
            {
                "picking_type_id": self.picking_type_out.id,
                "location_id": self.warehouse.lot_stock_id.id,
                "location_dest_id": self.env.ref("stock.stock_location_customers").id,
            }
        )
        move_out = self.env["stock.move"].create(
            {
                "name": "Move Out",
                "product_id": self.product.id,
                "product_uom_qty": 10,
                "product_uom": self.product.uom_id.id,
                "picking_id": picking_out.id,
                "location_id": picking_out.location_id.id,
                "location_dest_id": picking_out.location_dest_id.id,
                # link to incoming move
                "move_orig_ids": [Command.link(move_in.id)],
                # enable auto validate
                "auto_validate": auto_validate,
            }
        )
        # confirm pickings
        picking_in.action_confirm()
        picking_out.action_confirm()
        return picking_in, move_in, picking_out, move_out

    def test_01_without_auto_validate(self):
        picking_in, move_in, picking_out, move_out = self._create_pickings(
            auto_validate=False
        )
        # check states
        self.assertEqual(move_in.state, "assigned")
        self.assertEqual(move_out.state, "waiting")
        # process incoming picking
        move_in.quantity = 10
        move_in.picked = True
        picking_in.button_validate()
        # check incoming picking is done
        self.assertEqual(move_in.state, "done")
        self.assertEqual(picking_in.state, "done")
        # check outgoing picking is NOT done
        self.assertNotEqual(move_out.state, "done")
        self.assertNotEqual(picking_out.state, "done")
        # in standard flow, `move_out` should become assigned (or confirmed)
        # as `move_in` is done
        self.assertEqual(move_out.state, "assigned")
        self.assertEqual(picking_out.state, "assigned")

    def test_02_auto_validate(self):
        picking_in, move_in, picking_out, move_out = self._create_pickings(
            auto_validate=True
        )
        # check states
        self.assertEqual(move_in.state, "assigned")
        self.assertEqual(move_out.state, "waiting")
        # process incoming picking
        move_in.quantity = 10
        move_in.picked = True
        picking_in.button_validate()
        # check incoming picking is done
        self.assertEqual(move_in.state, "done")
        self.assertEqual(picking_in.state, "done")
        # check outgoing picking is done (auto validated)
        self.assertEqual(move_out.state, "done")
        self.assertEqual(picking_out.state, "done")
