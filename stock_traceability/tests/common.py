# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Jan 2026

import logging

from odoo import Command
from odoo.tests.common import TransactionCase, new_test_user

_logger = logging.getLogger(__name__)


class TestStockTraceabilityBase(TransactionCase):
    """Base class for Stock Traceability tests."""

    def _check_states(self, state_symbol_dict, model_name, field_name="state"):
        model = self.env[model_name]
        state_field = model._fields[field_name]
        states = [s[0] for s in state_field.selection]
        # ensure that all hard-coded states have a symbol match
        for state in states:
            self.assertIn(state, state_symbol_dict)
        # just check that no extra symbol is defined in the other way
        unknown_states = [s for s in state_symbol_dict.keys() if s not in states]
        if unknown_states:
            msg = f"`{model_name}` state symbol dict defined for unknown states:"
            for s in unknown_states:
                msg += f"\n\t- {s}"
            _logger.warning(msg)

    def _create_move(self, product, src_location, dst_location, **values):
        Move = self.env["stock.move"]  # .with_user(self.user_stock_manager)
        # set warehouse if not set and can be guessed from locations
        warehouse_id = src_location.warehouse_id or dst_location.warehouse_id
        if warehouse_id:
            values.setdefault("warehouse_id", warehouse_id.id)
        # simulate create + onchange
        move = Move.new(
            {
                "product_id": product.id,
                "location_id": src_location.id,
                "location_dest_id": dst_location.id,
            }
        )
        move._onchange_product_id()
        move_values = move._convert_to_write(move._cache)
        move_values.update(**values)
        move = Move.create(move_values)
        return move

    def _create_picking_move(self, product, picking, **values):
        values.setdefault("picking_id", picking.id)
        # set warehouse if not set and can be guessed from picking type
        if picking.picking_type_id.warehouse_id:
            values.setdefault("warehouse_id", picking.picking_type_id.warehouse_id.id)
        move = self._create_move(
            product,
            src_location=picking.location_id,
            dst_location=picking.location_dest_id,
            **values,
        )
        return move

    def _create_chained_moves(self, product, picking1, picking2, qty=10):
        # create move #1
        move1 = self._create_picking_move(
            product,
            picking1,
            name="Test Move (1/2)",
            product_uom_qty=qty,
        )
        # create move #2
        move2 = self._create_picking_move(
            product,
            picking2,
            name="Test Move (2/2)",
            product_uom_qty=qty,
            move_orig_ids=[Command.link(move1.id)],
        )
        return move1, move2

    def _new_group(self, name=False):
        procurement_group = self.env["procurement.group"].create(
            {
                "name": name or "Test Procurement Group",
            }
        )
        return procurement_group

    @classmethod
    def setUpClass(cls):
        super().setUpClass()

    def setUp(self):
        super().setUp()
        #
        ctx = {
            "mail_create_nolog": True,
            "mail_create_nosubscribe": True,
            "mail_notrack": True,
            "no_reset_password": True,
        }
        self.stock_user = new_test_user(
            self.env,
            login="stock_user",
            groups="stock.group_stock_user",
            context=ctx,
        )
        self.warehouse = self.env.ref("stock.warehouse0")
        # route_buy = warehouse.buy_pull_id.route_id
        # route_mto = warehouse.mto_pull_id.route_id
        # route_mto.active = True

        # locations
        self.location_stock = self.env.ref("stock.stock_location_stock")
        self.location_customers = self.env.ref("stock.stock_location_customers")
        self.location_supplier = self.env.ref("stock.stock_location_suppliers")
        # incoming picking
        self.picking_in = self.env["stock.picking"].create(
            {
                "picking_type_id": self.env.ref("stock.picking_type_in").id,
                "location_id": self.location_supplier.id,
                "location_dest_id": self.location_stock.id,
            }
        )
        # outgoing picking
        self.picking_out = self.env["stock.picking"].create(
            {
                "picking_type_id": self.env.ref("stock.picking_type_out").id,
                "location_id": self.location_stock.id,
                "location_dest_id": self.location_customers.id,
            }
        )
        # products
        self.product = self.env["product.product"].create(
            {
                "name": "Test Product",
                "type": "consu",
                "is_storable": True,
            }
        )
