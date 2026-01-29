# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Jan 2026

import logging

import freezegun

from odoo import Command
from odoo.tests.common import TransactionCase, new_test_user

from ..models.mail_activity import ACTIVITY_STATE_SYMBOLS
from ..models.mrp_production import PRODUCTION_STATE_SYMBOLS
from ..models.product import PRODUCT_TYPE_SYMBOLS
from ..models.purchase_order import PURCHASE_STATE_SYMBOLS
from ..models.stock_move import MOVE_STATE_SYMBOLS
from ..models.stock_picking import PICKING_STATE_SYMBOLS

_logger = logging.getLogger(__name__)


class TestStockTraceability(TransactionCase):
    """Tests for Stock Traceability module."""

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

    def test_03_production_states(self):
        """Tests that all hard-coded production states have a symbol match"""
        self._check_states(PRODUCTION_STATE_SYMBOLS, "mrp.production")

    def test_04_production_head_description(self):
        production = self.env["mrp.production"].create(
            {
                "product_id": self.env.ref("product.product_product_4").id,
                "product_qty": 5,
                "product_uom_id": self.env.ref("uom.product_uom_unit").id,
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

    def test_05_purchase_states(self):
        """Tests that all hard-coded purchase states have a symbol match"""
        self._check_states(PURCHASE_STATE_SYMBOLS, "purchase.order")

    def test_06_purchase_head_description(self):
        ctx = {
            "mail_create_nolog": True,
            "mail_create_nosubscribe": True,
            "mail_notrack": True,
            "no_reset_password": True,
        }
        purchase_user = new_test_user(
            self.env,
            login="action_view-user",
            groups="purchase.group_purchase_user",
            context=ctx,
        )
        purchase_order = (
            self.env["purchase.order"]
            .with_user(purchase_user)
            .create(
                {
                    "partner_id": self.env.ref("base.res_partner_12").id,
                    "order_line": [
                        Command.create(
                            {
                                "product_id": self.env.ref(
                                    "product.product_product_5"
                                ).id,
                                "product_qty": 10,
                                "product_uom": self.env.ref("uom.product_uom_unit").id,
                                "price_unit": 15.0,
                            },
                        )
                    ],
                }
            )
        )
        po_name = f"🛒{purchase_order.name}"
        head, desc = purchase_order.order_line[0].get_head_desc()
        self.assertEqual(head, po_name)
        self.assertEqual(desc, "🏳️RFQ")
        # change state to approved
        self.env.company.write(
            {
                "po_double_validation": "two_step",
                # require validation above 1.00 currency unit
                "po_double_validation_amount": 1.00,
            }
        )
        purchase_order.button_confirm()
        head, desc = purchase_order.order_line[0].get_head_desc()
        self.assertEqual(head, po_name)
        self.assertEqual(desc, "⏳To Approve")
        # approve and confirm
        purchase_order.with_user(self.env.user).button_approve()
        head, desc = purchase_order.order_line[0].get_head_desc()
        self.assertEqual(head, po_name)
        self.assertEqual(desc, "💲Purchase Order")
        # change state to done
        purchase_order.button_done()
        head, desc = purchase_order.order_line[0].get_head_desc()
        self.assertEqual(head, po_name)
        self.assertEqual(desc, "✅Locked")
        # change state to cancelled
        purchase_order.button_cancel()
        head, desc = purchase_order.order_line[0].get_head_desc()
        self.assertEqual(head, po_name)
        self.assertEqual(desc, "❌Cancelled")

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

    def test_30_(self):
        pass
