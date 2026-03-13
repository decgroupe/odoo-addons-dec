# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Apr 2025

from odoo import Command

from odoo.addons.mrp_stage.tests.common import TestMrpStageBase


class TestMrpSupplyProgress(TestMrpStageBase):
    """Tests for MRP Supply Progress module."""

    def setUp(self):
        super().setUp()
        self.partner = self.env["res.partner"].create({"name": "Test Supplier"})
        self.product2 = self._create_component_in_bom("#2", self.bom)
        self.product3 = self._create_component_in_bom("#3", self.bom)
        self.product4 = self._create_component_in_bom("#4", self.bom)

    def test_01_stock_move_received(self):
        production = self.env["mrp.production"].create(
            {
                "name": "WH/MO/TEST/01",
                "product_id": self.manufacturable_product.id,
                "product_uom_id": self.manufacturable_product.uom_id.id,
                "product_qty": 1,
            }
        )
        move1, move2, move3, move4 = production.move_raw_ids
        # confirm production order
        production.action_confirm()
        self.assertFalse(move1.received)
        self.assertFalse(move2.received)
        self.assertFalse(move3.received)
        self.assertFalse(move4.received)
        # actions on move 1
        move1.quantity = 1
        self.assertEqual(move2.state, "confirmed")
        self.assertTrue(move1.received)
        # actions on move 2
        move2.quantity = 1
        move2.picked = True
        move2._action_done()
        self.assertEqual(move2.state, "done")
        self.assertTrue(move2.received)
        # actions on move 3 (create a parent move)
        move3.procure_method = "make_to_order"
        pre_move3 = self.env["stock.move"].create(
            {
                "name": "Test Move",
                "product_id": move3.product_id.id,
                "product_uom": move3.product_uom.id,
                "product_uom_qty": move3.product_uom_qty,
                "location_id": self.warehouse1.lot_stock_id.id,
                "location_dest_id": move3.location_id.id,
                "procure_method": "make_to_stock",
                "move_dest_ids": [Command.link(move3.id)],
                # pre-fill ready to validate
                "picked": True,
                "quantity": move3.product_uom_qty,
            }
        )
        self.assertFalse(move3.received)
        pre_move3._action_done()
        self.assertTrue(move3.received)
        # actions on move 4 (create a parent move)
        move4.procure_method = "make_to_order"
        pre_move4 = self.env["stock.move"].create(
            {
                "name": "Test Move",
                "product_id": move4.product_id.id,
                "product_uom": move4.product_uom.id,
                "product_uom_qty": move4.product_uom_qty,
                "location_id": self.warehouse1.lot_stock_id.id,
                "location_dest_id": move4.location_id.id,
                "procure_method": "make_to_stock",
                "move_dest_ids": [Command.link(move4.id)],
            }
        )
        self.assertFalse(move4.received)
        # manually set "state" to "cancel" (otherwise `_action_cancel` will unset
        # `move_dest_ids` and set move4 procure method to MTS)
        # so ... this case is normally not possible in real life but we want to be sure
        # that the code is robust enough to handle it
        pre_move4.state = "cancel"
        self.assertTrue(move4.received)

    def test_02_production_progress(self):
        production = self.env["mrp.production"].create(
            {
                "name": "WH/MO/TEST/02",
                "product_id": self.manufacturable_product.id,
                "product_uom_id": self.manufacturable_product.uom_id.id,
                "product_qty": 1,
            }
        )
        move1, move2, move3, move4 = production.move_raw_ids
        self.assertFalse(production._allow_auto_start())
        # confirm production order
        production.action_confirm()
        # WARNING: the state becomes "progress" when the first raw move is "picked"
        self.assertEqual(production.stage_id.code, "confirmed")
        self.assertFalse(production._allow_auto_start())
        # check progress
        self.assertEqual(production.supply_progress, 0)
        move1.quantity = 1
        self.assertEqual(production.stage_id.code, "supplying")
        self.assertEqual(production.supply_progress, 25)
        move2.quantity = 1
        move3.quantity = 1
        self.assertEqual(production.stage_id.code, "supplying")
        self.assertEqual(production.supply_progress, 75)
        move4.quantity = 1
        self.assertEqual(production.supply_progress, 100)
        self.assertEqual(production.stage_id.code, "build_ready")
        self.assertTrue(production._allow_auto_start())

    def test_03_supply_progress_run_by_scheduler(self):
        production = self.env["mrp.production"].create(
            {
                "name": "WH/MO/TEST/03",
                "product_id": self.manufacturable_product.id,
                "product_uom_id": self.manufacturable_product.uom_id.id,
                "product_qty": 1,
            }
        )
        move1, move2, _move3, _move4 = production.move_raw_ids
        # confirm production order
        production.action_confirm()
        (move1 | move2).quantity = 1
        # manually override previous computation
        production.supply_progress = 0
        self.assertEqual(production.supply_progress, 0)
        # run scheduler
        self.production_model.run_supply_progress_update_scheduler()
        self.assertEqual(production.supply_progress, 50)

    def test_04_supply_progress_run_manually(self):
        production = self.env["mrp.production"].create(
            {
                "name": "WH/MO/TEST/04",
                "product_id": self.manufacturable_product.id,
                "product_uom_id": self.manufacturable_product.uom_id.id,
                "product_qty": 1,
            }
        )
        move1, move2, _move3, _move4 = production.move_raw_ids
        # confirm production order
        production.action_confirm()
        (move1 | move2).quantity = 1
        # manually override previous computation
        production.supply_progress = 0
        self.assertEqual(production.supply_progress, 0)
        # run manually
        production.action_update_supply_progress()
        self.assertEqual(production.supply_progress, 50)

    def test_05_kanban_show_progress(self):
        production = self.env["mrp.production"].create(
            {
                "name": "WH/MO/TEST/05",
                "product_id": self.manufacturable_product.id,
                "product_uom_id": self.manufacturable_product.uom_id.id,
                "product_qty": 1,
            }
        )
        production.bom_id = False
        # no progress when no raw moves
        self.assertFalse(production.move_raw_ids)
        self.assertFalse(production.kanban_show_supply_progress)
        # no progress is not supplying (draft)
        production.bom_id = self.bom
        self.assertTrue(len(production.move_raw_ids) > 0)
        self.assertEqual(production.stage_id.code, "draft")
        self.assertFalse(production.kanban_show_supply_progress)
        # confirm production order
        move1, move2, move3, move4 = production.move_raw_ids
        production.action_confirm()
        # no progress is not supplying (confirmed)
        self.assertEqual(production.stage_id.code, "confirmed")
        self.assertFalse(production.kanban_show_supply_progress)
        # set progress
        (move1 | move2).quantity = 1
        self.assertEqual(production.supply_progress, 50)
        self.assertEqual(production.stage_id.code, "supplying")
        self.assertTrue(production.kanban_show_supply_progress)
        # start manually
        production.action_start()
        self.assertEqual(production.supply_progress, 50)
        self.assertEqual(production.stage_id.code, "progress")
        self.assertTrue(production.kanban_show_supply_progress)
        # create an issue activity
        activity_id = production.activity_schedule(
            act_type_xmlid="mrp_stage.mail_activity_production_issue",
            summary="Test Issue",
        )
        move3.quantity = 1
        self.assertEqual(production.supply_progress, 75)
        self.assertEqual(production.stage_id.code, "issue")
        self.assertTrue(production.kanban_show_supply_progress)
        # set progress to 100%
        move4.quantity = 1
        self.assertEqual(production.supply_progress, 100)
        self.assertEqual(production.stage_id.code, "issue")
        self.assertFalse(production.kanban_show_supply_progress)
        # delete issue activity
        activity_id.unlink()
        self.assertEqual(production.supply_progress, 100)
        self.assertEqual(production.stage_id.code, "progress")
        self.assertFalse(production.kanban_show_supply_progress)
