# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Jan 2026

import logging

import freezegun

from odoo import Command

from ..models.mail_activity import ACTIVITY_STATE_SYMBOLS
from ..models.product import PRODUCT_TYPE_SYMBOLS
from ..models.stock_move import MOVE_STATE_SYMBOLS
from ..models.stock_picking import PICKING_STATE_SYMBOLS
from .common import TestStockTraceabilityBase

_logger = logging.getLogger(__name__)


class TestStockTraceability(TestStockTraceabilityBase):
    """Tests for Stock Traceability module."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()

    def setUp(self):
        super().setUp()

    def test_01_activity_states(self):
        """Tests that all hard-coded mail activity states have a symbol match"""
        self._check_states(ACTIVITY_STATE_SYMBOLS, "mail.activity")

    @freezegun.freeze_time("2017-01-12")
    def test_02_activity_head_description(self):
        product_id = self.env["product.product"].create(
            {
                "name": "Test Product",
                "type": "consu",
            }
        )
        activity = self.env["mail.activity"].create(
            {
                "note": "Test Activity of Test Product",
                "activity_type_id": self.env.ref("mail.mail_activity_data_todo").id,
                "summary": "Requires inventory",
                "res_id": product_id.product_tmpl_id.id,
                "res_model_id": self.env.ref("product.model_product_template").id,
            }
        )
        head, desc = activity.get_head_desc(product_id)
        self.assertEqual(head, "⚠️12/01/17:Test Activity of")
        self.assertEqual(desc, "✅Today")
        # change date to past
        activity.date_deadline = "2017-01-10"
        head, desc = activity.get_head_desc()
        self.assertEqual(head, "⚠️10/01/17:Test Activity of Test Product")
        self.assertEqual(desc, "🕸️Overdue")
        # change date to future
        activity.date_deadline = "2017-01-15"
        head, desc = activity.get_head_desc(product_id)
        self.assertEqual(head, "⚠️15/01/17:Test Activity of")
        self.assertEqual(desc, "📅Planned")
        activity.action_done()
        self.assertFalse(activity.exists())

    def test_07_product_types(self):
        """Tests that all hard-coded purchase states have a symbol match"""
        self._check_states(PRODUCT_TYPE_SYMBOLS, "product.template", field_name="type")

    def test_08_product_type_symbols(self):
        """Tests product type symbols"""
        product_model = self.env["product.product"]
        stockable = product_model.create(
            {
                "name": "Stockable Product",
                "type": "consu",
                "is_storable": True,
            }
        )
        consumable = product_model.create(
            {
                "name": "Consumable Product",
                "type": "consu",
            }
        )
        service = product_model.create(
            {
                "name": "Service Product",
                "type": "service",
            }
        )
        self.assertEqual(stockable.type_symbol, "➕")
        self.assertEqual(consumable.type_symbol, "🧃")
        self.assertEqual(service.type_symbol, "🛎️")

        combo_items = self.env["product.combo"].create(
            [
                {
                    "name": "Combo A",
                    "combo_item_ids": [Command.create({"product_id": consumable.id})],
                },
                {
                    "name": "Combo B",
                    "combo_item_ids": [Command.create({"product_id": service.id})],
                },
            ]
        )
        combo = product_model.create(
            {
                "name": "Combo Product",
                "type": "combo",
                "combo_ids": [Command.set(combo_items.ids)],
            }
        )
        self.assertEqual(combo.type_symbol, "🧩")

    def test_09_picking_states(self):
        """Tests that all hard-coded picking states have a symbol match"""
        self._check_states(PICKING_STATE_SYMBOLS, "stock.picking")

    def test_10_picking_head_description(self):
        picking = self.env["stock.picking"].create(
            {
                "picking_type_id": self.env.ref("stock.picking_type_in").id,
                "location_id": self.env.ref("stock.stock_location_stock").id,
                "location_dest_id": self.env.ref("stock.stock_location_customers").id,
            }
        )
        head, desc = picking.get_head_desc()
        self.assertEqual(head, f"🗳️{picking.name}")
        self.assertEqual(desc, "🏳️Draft")
        # add some move lines for [FURN_1118] Corner Desk Left Sit
        product = self.env.ref("product.product_product_13")

        # warehouse = self.env.ref("stock.warehouse0")
        # route_buy = warehouse.buy_pull_id.route_id
        # route_mto = warehouse.mto_pull_id.route_id
        # route_mto.active = True
        # product.route_ids = [Command.link(route_buy.id), Command.link(route_mto.id)]

        move = self.env["stock.move"].create(
            {
                "name": "Test Move",
                "product_id": product.id,
                "product_uom_qty": 10,
                "product_uom": product.uom_id.id,
                "picking_id": picking.id,
                "location_id": picking.location_id.id,
                "location_dest_id": picking.location_dest_id.id,
                "procure_method": "make_to_order",  # to force `waiting` state
            }
        )
        # change state to confirmed
        picking.action_confirm()
        head, desc = picking.get_head_desc()
        self.assertEqual(head, f"🗳️{picking.name}")
        self.assertEqual(desc, "⛓️Waiting Another Operation")
        # change state to assigned
        move.quantity = move.product_uom_qty
        picking.action_assign()
        head, desc = picking.get_head_desc()
        self.assertEqual(head, f"🗳️{picking.name}")
        self.assertEqual(desc, "✳️Ready")
        # change state to done
        move.picked = True
        picking.action_done()
        head, desc = picking.get_head_desc()
        self.assertEqual(head, f"🗳️{picking.name}")
        self.assertEqual(desc, "✅Done")
        # change state to done
        move.state = "assigned"  # for testing purpose only
        picking.action_cancel()
        head, desc = picking.get_head_desc()
        self.assertEqual(head, f"🗳️{picking.name}")
        self.assertEqual(desc, "❌Cancelled")

    def test_11_move_states(self):
        """Tests that all hard-coded stock move states have a symbol match"""
        self._check_states(MOVE_STATE_SYMBOLS, "stock.move")

    def test_12_move_mts_head_description(self):
        picking = self.env["stock.picking"].create(
            {
                "picking_type_id": self.env.ref("stock.picking_type_in").id,
                "location_id": self.env.ref("stock.stock_location_stock").id,
                "location_dest_id": self.env.ref("stock.stock_location_customers").id,
            }
        )
        # add some move lines for new product
        product = self.env["product.product"].create(
            {"name": "Test Product", "type": "consu", "is_storable": True}
        )
        # set stock available quantity to 10
        # self.env["stock.quant"]._update_available_quantity(
        #     product, picking.location_id, 10
        # )
        move = self.env["stock.move"].create(
            {
                "name": "Test Move",
                "product_id": product.id,
                "product_uom_qty": 10,
                "product_uom": product.uom_id.id,
                "picking_id": picking.id,
                "location_id": picking.location_id.id,
                "location_dest_id": picking.location_dest_id.id,
            }
        )
        mts_head = "📦Stock"
        # initial move state is draft
        head, desc = move.get_head_desc()
        self.assertEqual(head, mts_head)
        self.assertEqual(desc, "🏳️New")
        # change state to confirmed
        picking.action_confirm()
        head, desc = move.get_head_desc()
        self.assertEqual(head, mts_head)
        self.assertEqual(desc, "⏳Waiting Availability")
        # change state to partially available
        move.quantity = 1.0
        head, desc = move.get_head_desc()
        self.assertEqual(head, mts_head)
        self.assertEqual(desc, "✴️Partially Available")
        # change state to assigned (aka available)
        move.quantity = move.product_uom_qty
        head, desc = move.get_head_desc()
        self.assertEqual(head, mts_head)
        self.assertEqual(desc, "✳️Available")
        # change state to done
        move.picked = True
        picking.action_done()
        head, desc = move.get_head_desc()
        self.assertEqual(head, mts_head)
        self.assertEqual(desc, "✅Done")
        # change state to done
        move.state = "assigned"  # for testing purpose only
        picking.action_cancel()
        head, desc = move.get_head_desc()
        self.assertEqual(head, mts_head)
        self.assertEqual(desc, "❌Cancelled")

    def test_13_move_mto_head_description(self):
        picking = self.env["stock.picking"].create(
            {
                "picking_type_id": self.env.ref("stock.picking_type_in").id,
                "location_id": self.env.ref("stock.stock_location_stock").id,
                "location_dest_id": self.env.ref("stock.stock_location_customers").id,
            }
        )
        # add some move lines for [FURN_1118] Corner Desk Left Sit
        product = self.env.ref("product.product_product_13")
        move = self.env["stock.move"].create(
            {
                "name": "Test Move",
                "product_id": product.id,
                "product_uom_qty": 10,
                "product_uom": product.uom_id.id,
                "picking_id": picking.id,
                "location_id": picking.location_id.id,
                "location_dest_id": picking.location_dest_id.id,
                "procure_method": "make_to_order",  # to force `waiting` state
            }
        )
        mto_head = "❓make_to_order"
        # initial move state is draft
        head, desc = move.get_head_desc()
        self.assertEqual(head, mto_head)
        self.assertEqual(desc, "🏳️New")
        # change state to confirmed
        picking.action_confirm()
        head, desc = move.get_head_desc()
        self.assertEqual(head, mto_head)
        self.assertEqual(desc, "⛓️Waiting Another Move")
        # change state to partially available
        move.quantity = 1.0
        head, desc = move.get_head_desc()
        self.assertEqual(head, mto_head)
        self.assertEqual(desc, "✴️Partially Available")
        # change state to assigned (aka available)
        move.quantity = move.product_uom_qty
        head, desc = move.get_head_desc()
        self.assertEqual(head, mto_head)
        self.assertEqual(desc, "✳️Available")
        # change state to done
        move.picked = True
        picking.action_done()
        head, desc = move.get_head_desc()
        self.assertEqual(head, mto_head)
        self.assertEqual(desc, "✅Done")
        # change state to done
        move.state = "assigned"  # for testing purpose only
        picking.action_cancel()  # move `procure_method` converted to "MTS"
        head, desc = move.get_head_desc()
        self.assertEqual(head, "📦Stock")
        self.assertEqual(desc, "❌Cancelled")

    def test_20_procurement_group_head(self):
        """Tests procurement group head and description generation"""
        procurement_group = self.env["procurement.group"].create(
            {
                "name": "Test Procurement Group",
            }
        )
        head, desc = procurement_group.get_head_desc()
        self.assertEqual(head, "📋Test Procurement Group")
        self.assertFalse(desc)
