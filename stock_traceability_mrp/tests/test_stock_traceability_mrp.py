# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Mar 2026

import logging

from odoo import Command

from ..models.mrp_production import PRODUCTION_STATE_SYMBOLS
from .common import TestStockTraceabilityMrpBase

_logger = logging.getLogger(__name__)


class TestStockTraceabilityMrp(TestStockTraceabilityMrpBase):
    """Tests for Stock Traceability module."""

    def test_01_production_states(self):
        """Tests that all hard-coded production states have a symbol match"""
        self._check_states(PRODUCTION_STATE_SYMBOLS, "mrp.production")

    def test_02_production_head_description(self):
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

    def test_03_create_another_production_from_bom(self):
        production = self.env["mrp.production"].create(
            {
                "name": "WH/MO/TEST/03/01",
                "product_id": self.manufacturable_product.id,
                "product_uom_id": self.manufacturable_product.uom_id.id,
                "product_qty": 1,
            }
        )
        single_move = production.move_raw_ids
        self.assertEqual(len(single_move), 1)
        self.assertEqual(single_move.state, "draft")
        self.assertEqual(single_move.procure_method, "make_to_stock")
        # set our product as manufacturable
        self.product.route_ids = [
            Command.set([self.route_mto.id, self.route_manufacture.id])
        ]
        # test status
        self.assertEqual(
            single_move.mrp_status,
            '<div class="d_move d_move_draft"><ul><li>➕Goods</li>'
            "<li>📦Stock <small>🏳️New</small></li></ul></div>",
        )
        # test plain text version
        self.assertEqual(
            single_move.get_mrp_status(html=False),
            "➕Goods\n📦Stock 🏳️New",
        )
        # confirm production order
        production.action_confirm()
        self.assertEqual(single_move.state, "waiting")
        # the move should be automatically set to MTO
        self.assertEqual(single_move.procure_method, "make_to_order")
        # a new production order must be created
        self.assertTrue(single_move.created_production_id)
        next_production = single_move.created_production_id
        # override the name to avoid randomization in tests (note that the archived name
        # is still the original one in single_move.created_productions_archive)
        next_production.name = "WH/MO/TEST/03/02"
        self.assertEqual(next_production.product_id, self.product)
        # this new production order should have one move to finished and no raw moves
        self.assertEqual(len(next_production.move_raw_ids), 0)
        self.assertEqual(len(next_production.move_finished_ids), 1)
        # this move to finish must be mapped to the original move
        self.assertEqual(next_production.move_finished_ids, single_move.move_orig_ids)
        # so the counterpart must be true
        self.assertEqual(next_production, single_move.move_orig_ids.production_id)
        # test updated status
        self.assertEqual(
            single_move.mrp_status,
            '<div class="d_move d_move_waiting"><ul><li>➕Goods</li>'
            "<li>🔧WH/MO/TEST/03/02 <small>✨Draft</small></li></ul></div>",
        )
        # test plain text version
        self.assertEqual(
            single_move.get_mrp_status(html=False),
            "➕Goods\n🔧WH/MO/TEST/03/02 ✨Draft",
        )
        next_finished_move = next_production.move_finished_ids
        # both pick and mrp status are identical for a move waiting for a production
        txt_status = "➕Goods\n📦Stock 🏳️New"
        self.assertEqual(next_finished_move.get_pick_status(html=False), txt_status)
        self.assertEqual(next_finished_move.get_mrp_status(html=False), txt_status)
        # cancel production and test status update on the waiting move
        next_production.action_cancel()
        self.assertEqual(
            next_finished_move.get_pick_status(html=False),
            "➕Goods\n📦Stock ❌Cancelled\n🗺️Location Not Set",
        )
        txt_status = "➕Goods\n📦Stock ⏳Waiting Availability\n♻️MO/canceled"
        self.assertEqual(single_move.get_mrp_status(html=False), txt_status)
        # the move should be automatically converted to MTO
        self.assertEqual(single_move.procure_method, "make_to_stock")
        # delete the production and check that mrp status is still valid
        next_production.unlink()
        self.assertEqual(single_move.get_mrp_status(html=False), txt_status)
        # validate html status
        html_status = (
            '<div class="d_move d_move_confirmed"><ul><li>➕Goods</li>'
            "<li>📦Stock <small>⏳Waiting Availability</small></li>"
            "<li>♻️MO/canceled</li></ul></div>"
        )
        self.assertEqual(single_move.mrp_status, html_status)
        self.assertEqual(single_move.pick_status, html_status)

    def test_05_archive_created_productions(self):
        """Test archiving from `stock.move` create/write, since real archiving is
        commonly done in `production.order` write when `move_dest_ids` is updated.
        """
        production = self.env["mrp.production"].create(
            {
                "name": "WH/MO/TEST/05/01",
                "product_id": self.manufacturable_product.id,
                "product_uom_id": self.manufacturable_product.uom_id.id,
                "product_qty": 1,
            }
        )
        next_production1 = self.env["mrp.production"].create(
            {
                "name": "WH/MO/TEST/05/02",
                "product_id": self.product.id,
                "product_uom_id": self.product.uom_id.id,
                "product_qty": 1,
            }
        )
        next_production1.action_confirm()
        # manually link the finished move to our first production order component
        # to simulate the creation of a production from a move
        production.move_raw_ids.created_production_id = next_production1
        # cancel this production and create a new one from the same move
        next_production1.action_cancel()
        next_production2 = self.env["mrp.production"].create(
            {
                "name": "WH/MO/TEST/05/03",
                "product_id": self.product.id,
                "product_uom_id": self.product.uom_id.id,
                "product_qty": 1,
            }
        )
        next_production2.action_confirm()
        # manually link the finished move to our first production order component
        # to simulate the creation of a production from a move
        production.move_raw_ids.created_production_id = next_production2
        archives = list(production.move_raw_ids.created_productions_archive.values())
        self.assertEqual(len(archives), 2)
        self.assertIn(next_production1.name, archives)
        self.assertIn(next_production2.name, archives)
