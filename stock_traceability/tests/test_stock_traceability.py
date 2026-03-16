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

        # create a fake "supply" route without implying "manufacture" or "buy" rules
        # to avoid dependencies with other modules in our tests
        self.route_pull_from_supplier = self.env["stock.route"].create(
            {
                "name": "PFV",
                "active": True,
                "product_selectable": True,
            }
        )
        _pfv_rule = self.env["stock.rule"].create(
            {
                "route_id": self.route_pull_from_supplier.id,
                "warehouse_id": self.warehouse.id,
                "name": "PFV Rule",
                "picking_type_id": self.env.ref("stock.picking_type_in").id,
                "location_src_id": self.location_supplier.id,
                "location_dest_id": self.location_stock.id,
                "procure_method": "make_to_stock",
            }
        )

    def test_01_activity_states(self):
        """Tests that all hard-coded mail activity states have a symbol match"""
        self._check_states(ACTIVITY_STATE_SYMBOLS, "mail.activity")

    @freezegun.freeze_time("2017-01-12")
    def test_02_activity_head_description(self):
        activity = self.env["mail.activity"].create(
            {
                "note": "Test Activity of Test Product",
                "activity_type_id": self.env.ref("mail.mail_activity_data_todo").id,
                "summary": "Requires inventory",
                "res_id": self.product.product_tmpl_id.id,
                "res_model_id": self.env.ref("product.model_product_template").id,
            }
        )
        head, desc = activity.get_head_desc(self.product)
        self.assertEqual(head, "⚠️12/01/17:Test Activity of")
        self.assertEqual(desc, "✅Today")
        # change date to past
        activity.date_deadline = "2017-01-10"
        head, desc = activity.get_head_desc()
        self.assertEqual(head, "⚠️10/01/17:Test Activity of Test Product")
        self.assertEqual(desc, "🕸️Overdue")
        # change date to future
        activity.date_deadline = "2017-01-15"
        head, desc = activity.get_head_desc(self.product)
        self.assertEqual(head, "⚠️15/01/17:Test Activity of")
        self.assertEqual(desc, "📅Planned")
        activity.action_done()
        self.assertFalse(activity.exists())

    def test_03_product_types(self):
        """Tests that all hard-coded purchase states have a symbol match"""
        self._check_states(PRODUCT_TYPE_SYMBOLS, "product.template", field_name="type")

    def test_04_product_type_symbols(self):
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

    def test_05_picking_states(self):
        """Tests that all hard-coded picking states have a symbol match"""
        self._check_states(PICKING_STATE_SYMBOLS, "stock.picking")

    def test_06_picking_head_description(self):
        # check default head description
        head, desc = self.picking_out.get_head_desc()
        self.assertEqual(head, f"🗳️{self.picking_out.name}")
        self.assertEqual(desc, "🏳️Draft")
        # set fake supply route
        self.product.route_ids = [Command.link(self.route_pull_from_supplier.id)]
        # add some move lines for our test product
        move = self._create_picking_move(
            self.product,
            self.picking_out,
            name="Test Move",
            product_uom_qty=10,
            procure_method="make_to_order",  # to force `waiting` state
        )
        # change state to confirmed
        self.picking_out.action_confirm()
        head, desc = self.picking_out.get_head_desc()
        self.assertEqual(head, f"🗳️{self.picking_out.name}")
        self.assertEqual(desc, "⛓️Waiting Another Operation")
        # change state to assigned
        move.quantity = move.product_uom_qty
        self.picking_out.action_assign()
        head, desc = self.picking_out.get_head_desc()
        self.assertEqual(head, f"🗳️{self.picking_out.name}")
        self.assertEqual(desc, "✳️Ready")
        # change state to done
        move.picked = True
        self.picking_out.action_done()
        head, desc = self.picking_out.get_head_desc()
        self.assertEqual(head, f"🗳️{self.picking_out.name}")
        self.assertEqual(desc, "✅Done")
        # change state to done
        move.state = "assigned"  # for testing purpose only
        self.picking_out.action_cancel()
        head, desc = self.picking_out.get_head_desc()
        self.assertEqual(head, f"🗳️{self.picking_out.name}")
        self.assertEqual(desc, "❌Cancelled")

    def test_07_move_states(self):
        """Tests that all hard-coded stock move states have a symbol match"""
        self._check_states(MOVE_STATE_SYMBOLS, "stock.move")

    def test_08_move_mts_head_description(self):
        # set stock available quantity to 10
        # self.env["stock.quant"]._update_available_quantity(
        #     self.product, self.picking_out.location_id, 10
        # )
        # add some move lines for new product
        move = self._create_picking_move(
            self.product,
            self.picking_out,
            name="Test Move",
            product_uom_qty=10,
        )
        mts_head = "📦Stock"
        # initial move state is draft
        head, desc = move.get_head_desc()
        self.assertEqual(head, mts_head)
        self.assertEqual(desc, "🏳️New")
        # change state to confirmed
        self.picking_out.action_confirm()
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
        self.picking_out.action_done()
        head, desc = move.get_head_desc()
        self.assertEqual(head, mts_head)
        self.assertEqual(desc, "✅Done")
        # change state to done
        move.state = "assigned"  # for testing purpose only
        self.picking_out.action_cancel()
        head, desc = move.get_head_desc()
        self.assertEqual(head, mts_head)
        self.assertEqual(desc, "❌Cancelled")

    def test_09_move_mto_head_description(self):
        # set fake supply route
        self.product.route_ids = [Command.link(self.route_pull_from_supplier.id)]
        # add some move lines for our test product
        move = self._create_picking_move(
            self.product,
            self.picking_out,
            name="Test Move",
            product_uom_qty=10,
            procure_method="make_to_order",
        )
        mto_head = "👽MTO"
        # initial move state is draft
        head, desc = move.get_head_desc()
        self.assertEqual(head, mto_head)
        self.assertEqual(desc, "🏳️New")
        # change state to confirmed
        self.picking_out.action_confirm()
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
        self.picking_out.action_done()
        head, desc = move.get_head_desc()
        self.assertEqual(head, mto_head)
        self.assertEqual(desc, "✅Done")
        # change state to done
        move.state = "assigned"  # for testing purpose only
        self.picking_out.action_cancel()  # move `procure_method` converted to "MTS"
        head, desc = move.get_head_desc()
        self.assertEqual(head, "📦Stock")
        self.assertEqual(desc, "❌Cancelled")

    def test_10_procurement_group_head(self):
        """Tests procurement group head and description generation"""
        procurement_group = self._new_group()
        head, desc = procurement_group.get_head_desc()
        self.assertEqual(head, "📋")
        self.assertEqual(desc, "Test Procurement Group")

    def test_11_move_get_stock_location(self):
        """Tests _get_stock_location method with and without location fields"""
        move = self._create_picking_move(
            self.product,
            self.picking_out,
            name="Test Move",
            product_uom_qty=10,
        )
        # test without location fields set
        head, desc = move._get_stock_location(html=False)
        self.assertIn("Not Set", desc)
        self.assertIn("Location", head)
        # test with location fields set
        self.product.loc_rack = "Rack A"
        head, desc = move._get_stock_location(html=False)
        self.assertIn("Rack A", desc)
        # test HTML version
        head, desc = move._get_stock_location(html=True)
        self.assertIn("Location", head)

    def test_12_move_format_status_header(self):
        """Tests _format_status_header with and without HTML"""
        move = self._create_picking_move(
            self.product,
            self.picking_out,
            name="Test Move",
            product_uom_qty=10,
        )
        status = ["Status Line 1", "Status Line 2"]
        # test plain text format
        result = move._format_status_header(status, html=False)
        self.assertIn("Status Line 1", result)
        self.assertIn("Status Line 2", result)
        # test HTML format
        result = move._format_status_header(status, html=True)
        self.assertIn("<div", result)

    def test_13_move_get_upstreams(self):
        """Tests _get_upstreams method with product matching"""
        # create incoming/outgoing moves
        move_in, move_out = self._create_chained_moves(
            self.product, self.picking_in, self.picking_out
        )
        # test with product matching
        upstreams = move_out._get_upstreams(ensure_same_product=True)
        self.assertIn(move_in, upstreams)
        # test without product matching
        upstreams = move_out._get_upstreams(ensure_same_product=False)
        self.assertIn(move_in, upstreams)

    def test_14_move_get_pre_header(self):
        """Tests _get_pre_header with different product types"""
        product_consu = self.env["product.product"].create(
            {"name": "Consumable Product", "type": "consu", "is_storable": False}
        )
        product_service = self.env["product.product"].create(
            {"name": "Service Product", "type": "service"}
        )
        move_consu = self._create_picking_move(
            product_consu,
            self.picking_out,
            name="Test Move Consu",
            product_uom_qty=10,
        )
        move_service = self._create_picking_move(
            product_service,
            self.picking_out,
            name="Test Move Service",
            product_uom_qty=10,
        )
        # test consumable product header
        header_consu = move_consu._get_pre_header()
        self.assertEqual(header_consu, "🧃Goods")
        # test service product header
        header_service = move_service._get_pre_header()
        self.assertEqual(header_service, "🛎️Service")

    def test_15_move_action_open_stock_move_form(self):
        """Tests action_open_stock_move_form returns correct action"""
        move = self._create_picking_move(
            self.product,
            self.picking_out,
            name="Test Move",
            product_uom_qty=10,
        )
        action = move.action_open_stock_move_form()
        self.assertEqual(action["type"], "ir.actions.act_window")
        self.assertEqual(action["res_model"], "stock.move")
        self.assertEqual(action["res_id"], move.id)
        self.assertEqual(action["view_mode"], "form")

    def test_16_move_action_close_dialog(self):
        """Tests action_close_dialog returns correct action"""
        move = self._create_picking_move(
            self.product,
            self.picking_out,
            name="Test Move",
            product_uom_qty=10,
        )
        action = move.action_close_dialog()
        self.assertEqual(action["type"], "ir.actions.act_window_close")

    def test_17_move_final_location_single_dest(self):
        """Tests _compute_final_location with single destination move"""
        move_in, move_out = self._create_chained_moves(
            self.product, self.picking_in, self.picking_out
        )
        # check initial final location
        self.assertEqual(move_out.final_location, "Customers")
        self.assertEqual(move_in.final_location, "Stock > Customers")
        # basic user should see location names only
        move_in = move_in.with_user(self.stock_user)
        move_in.invalidate_recordset()
        self.assertEqual(move_in.final_location, "Customers")

    def test_18_move_action_view_without_created_item(self):
        """Tests action_view_created_item without created item"""
        move = self._create_picking_move(
            self.product,
            self.picking_out,
            name="Test Move",
            product_uom_qty=10,
        )
        # without activity/created item it should be False
        self.assertFalse(move.action_view_created_item_visible)
        # test without created item
        action = move.action_view_created_item()
        self.assertFalse(action)

    def test_19_move_get_assignable_status_waiting_state(self):
        """Tests _get_assignable_status with waiting state"""
        # create incoming/outgoing moves
        _move_in, move_out = self._create_chained_moves(
            self.product, self.picking_in, self.picking_out
        )
        # confirm both pickings
        self.picking_in.action_confirm()
        self.picking_out.action_confirm()
        # cancel the incoming move to trigger assignable status check
        self.picking_in.action_cancel()
        # test assignable status
        status = move_out._get_assignable_status(html=False)
        self.assertIsInstance(status, list)

    def test_20_move_get_pick_status(self):
        """Tests get_pick_status"""
        # create MTS move
        move_mts = self._create_picking_move(
            self.product, self.picking_out, name="Test MTS Move"
        )
        self.assertEqual(
            move_mts.pick_status,
            '<div class="d_move d_move_draft"><ul><li>➕Goods</li>'
            "<li>📦Stock <small>🏳️New</small></li></ul></div>",
        )
        # test plain text version
        mts_status = move_mts.get_pick_status(html=False)
        self.assertEqual(mts_status, "➕Goods\n📦Stock 🏳️New")
        # create MTO move
        move_mto = self._create_picking_move(
            self.product,
            self.picking_out,
            name="Test MTO Move",
            procure_method="make_to_order",
        )
        self.assertEqual(
            move_mto.pick_status,
            '<div class="d_move d_move_draft"><ul><li>➕Goods</li>'
            "<li>👽MTO <small>🏳️New</small></li></ul></div>",
        )
        # test plain text version
        mto_status = move_mto.get_pick_status(html=False)
        self.assertEqual(mto_status, "➕Goods\n👽MTO 🏳️New")

    @freezegun.freeze_time("2017-01-12")
    def test_21_chained_mts2mto_move_get_pick_status(self):
        """Tests get_pick_status for chained moves.
        We do not confirm pickings to trigger MTO status as moves will be cancelled
        since no other module are installed with MTO support.
        """
        # create incoming/outgoing moves
        self.picking_in.name = "WH/IN/TEST/0001"
        self.picking_out.name = "WH/OUT/TEST/0001"
        move_in, move_out = self._create_chained_moves(
            self.product, self.picking_in, self.picking_out
        )
        move_in.group_id = self._new_group("#A")
        move_out.group_id = self._new_group("#B")
        move_out.procure_method = "make_to_order"
        # test status for move_in
        move_in_status = move_in.get_pick_status(html=False)
        self.assertEqual(
            move_in_status,
            "➕Goods\n📦Stock 🏳️New\n📥📋 #B",
        )
        # test status for move_out
        move_out_status = move_out.get_pick_status(html=False)
        self.assertEqual(
            move_out_status,
            "➕Goods\n👽MTO 🏳️New\n🚚 WH/IN/TEST/0001 2017-01-12\n"
            "📦Stock 🏳️New\n📤📋 #A",
        )

    @freezegun.freeze_time("2017-01-12")
    def test_22_chained_mto2mts_move_get_pick_status(self):
        """Tests get_pick_status for chained moves.
        We do not confirm pickings to trigger MTO status as moves will be cancelled
        since no other module are installed with MTO support.
        """
        # create incoming/outgoing moves
        self.picking_in.name = "WH/IN/TEST/0001"
        self.picking_out.name = "WH/OUT/TEST/0001"
        move_in, move_out = self._create_chained_moves(
            self.product, self.picking_in, self.picking_out
        )
        move_in.group_id = self._new_group("#A")
        move_in.procure_method = "make_to_order"
        move_out.group_id = self._new_group("#B")
        # test status for move_in
        move_in_status = move_in.get_pick_status(html=False)
        self.assertEqual(
            move_in_status,
            "➕Goods\n👽MTO 🏳️New\n📥📋 #B",
        )
        # test status for move_out
        move_out_status = move_out.get_pick_status(html=False)
        self.assertEqual(
            move_out_status,
            "➕Goods\n📦Stock 🏳️New\n👽MTO 🏳️New\n📤📋 #A",
        )

    @freezegun.freeze_time("2017-01-12")
    def test_23_move_product_activity_id(self):
        """Tests _compute_product_activity_id when activity exists"""
        move = self._create_picking_move(
            self.product,
            self.picking_out,
            name="Test Move for Activity",
        )
        self.assertFalse(move.product_activity_id)
        # create activity
        activity = self.env["mail.activity"].create(
            {
                "activity_type_id": self.env.ref("mail.mail_activity_data_warning").id,
                "res_id": self.product.product_tmpl_id.id,
                "res_model_id": self.env.ref("product.model_product_template").id,
            }
        )
        # recompute to ensure activity is found
        move.invalidate_recordset()
        self.assertEqual(move.product_activity_id, activity)
        self.assertEqual(
            move.pick_status,
            '<div class="d_move d_move_draft"><ul><li>➕Goods</li>'
            "<li>📦Stock <small>🏳️New</small></li>"
            "<li>⚠️12/01/17: <small>✅Today</small></li></ul></div>",
        )
        # test plain text version
        pick_status = move.get_pick_status(html=False)
        self.assertEqual(
            pick_status,
            "➕Goods\n📦Stock 🏳️New\n⚠️12/01/17: ✅Today",
        )
        # updated status
        self.picking_out.action_confirm()
        pick_status = move.get_pick_status(html=False)
        self.assertEqual(
            pick_status,
            "➕Goods\n📦Stock ⏳Waiting Availability\n⚠️12/01/17: ✅Today",
        )
        # with an activity/created item it should be True
        self.assertTrue(move.action_view_created_item_visible)
        # test created item
        action = move.action_view_created_item()
        self.assertEqual(action["type"], "ir.actions.act_window")
        created_item = move._get_mto_created_item()
        self.assertEqual(created_item["action"], action)
        self.assertEqual(created_item["priority"], 10)
        self.assertEqual(created_item["record"], activity)
        # change move to MTO
        move.procure_method = "make_to_order"
        move.invalidate_recordset()
        self.assertEqual(move.product_activity_id, activity)
        self.assertEqual(
            move.pick_status,
            '<div class="d_move d_move_confirmed"><ul><li>➕Goods</li>'
            "<li>⚠️12/01/17: <small>✅Today</small></li></ul></div>",
        )
        # test plain text version
        pick_status = move.get_pick_status(html=False)
        self.assertEqual(
            pick_status,
            "➕Goods\n⚠️12/01/17: ✅Today",
        )
