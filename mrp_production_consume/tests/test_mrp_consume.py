# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by GitHub Copilot <copilot at github.com>, Mar 2026


from .common import TestMrpConsumeBase


class TestMrpConsume(TestMrpConsumeBase):
    """Test cases for MRP Consume wizard."""

    @classmethod
    def setUpClass(cls):
        """Set up test data."""
        super().setUpClass()

    def test_01_default_get_initialization(self):
        """Test that without `active_id`, default_get does not properly initializes
        wizard."""
        # create and confirm production
        production = self.env["mrp.production"].create(
            {
                "product_id": self.product.id,
                "product_qty": 1,
                "bom_id": self.bom.id,
            }
        )
        production.action_confirm()
        # create consume wizard
        consume = self.env["mrp.consume"].create(
            {
                "production_id": production.id,
            }
        )
        # verify initialization
        self.assertEqual(consume.production_id, production)
        self.assertEqual(consume.company_id, production.company_id)
        self.assertFalse(consume.product_id)
        self.assertFalse(consume.product_qty)

    def test_02_default_get_with_context(self):
        """Test default_get with active_id context."""
        # create and confirm production
        production = self.env["mrp.production"].create(
            {
                "product_id": self.product.id,
                "product_qty": 2,
                "bom_id": self.bom.id,
            }
        )
        production.action_confirm()
        # call default_get with context
        wizard_model = self.env["mrp.consume"]
        defaults = wizard_model.with_context(active_id=production.id).default_get(
            [
                "production_id",
                "product_id",
                "product_qty",
                "product_uom_id",
            ]
        )
        # verify defaults are set correctly
        self.assertEqual(defaults["production_id"], production.id)
        self.assertEqual(defaults["product_id"], self.product.id)
        self.assertEqual(defaults["product_qty"], 2)
        self.assertEqual(defaults["product_uom_id"], production.product_uom_id.id)

    def test_03_onchange_product_qty(self):
        """Test _onchange_product_qty creates consumption lines."""
        # create and confirm production
        production = self.env["mrp.production"].create(
            {
                "product_id": self.product.id,
                "product_qty": 1,
                "bom_id": self.bom.id,
            }
        )
        production.action_confirm()
        # create consume wizard
        consume = self.env["mrp.consume"].create(
            {
                "production_id": production.id,
                "product_id": self.product.id,
                "product_uom_id": production.product_uom_id.id,
                "product_qty": 1,
            }
        )
        # trigger onchange
        consume._onchange_product_qty()
        # verify consumption lines are created
        self.assertEqual(len(consume.line_ids), 3)
        # verify quantities
        for line in consume.line_ids:
            self.assertGreater(line.qty_to_consume, 0)
            self.assertEqual(line.qty_done, 0)

    def test_04_get_updated_move_ids(self):
        """Test _get_updated_move_ids retrieves updated moves."""
        # create and confirm production
        production = self.env["mrp.production"].create(
            {
                "product_id": self.product.id,
                "product_qty": 1,
                "bom_id": self.bom.id,
            }
        )
        production.action_confirm()
        # create consume wizard with lines
        consume = self.env["mrp.consume"].create(
            {
                "production_id": production.id,
                "product_id": self.product.id,
                "product_uom_id": production.product_uom_id.id,
                "product_qty": 1,
            }
        )
        consume._onchange_product_qty()
        # set quantities done on some lines
        for i, line in enumerate(consume.line_ids):
            if i < 2:
                line.qty_done = 1
        # get updated moves
        move_ids = consume._get_updated_move_ids()
        # verify correct moves are returned
        self.assertEqual(len(move_ids), 2)

    def test_05_get_updated_move_ids_empty(self):
        """Test _get_updated_move_ids returns empty when no qty_done."""
        # create and confirm production
        production = self.env["mrp.production"].create(
            {
                "product_id": self.product.id,
                "product_qty": 1,
                "bom_id": self.bom.id,
            }
        )
        production.action_confirm()
        # create consume wizard
        consume = self.env["mrp.consume"].create(
            {
                "production_id": production.id,
                "product_id": self.product.id,
                "product_uom_id": production.product_uom_id.id,
                "product_qty": 1,
            }
        )
        consume._onchange_product_qty()
        # get updated moves without setting qty_done
        move_ids = consume._get_updated_move_ids()
        # should return empty set
        self.assertEqual(len(move_ids), 0)

    def test_06_do_consume_basic(self):
        """Test do_consume basic workflow."""
        # create and confirm production
        production = self.env["mrp.production"].create(
            {
                "product_id": self.product.id,
                "product_qty": 1,
                "bom_id": self.bom.id,
            }
        )
        production.action_confirm()
        initial_state = production.state
        self.assertEqual(initial_state, "confirmed")
        # create consume wizard
        consume = self.env["mrp.consume"].create(
            {
                "production_id": production.id,
                "product_id": self.product.id,
                "product_uom_id": production.product_uom_id.id,
                "product_qty": 1,
            }
        )
        consume._onchange_product_qty()
        # set quantities
        for line in consume.line_ids:
            line.qty_done = line.qty_to_consume
        # execute consume
        result = consume.do_consume()
        # verify result is close window action
        self.assertEqual(result["type"], "ir.actions.act_window_close")
        # verify production moved to progress
        self.assertEqual(production.state, "progress")

    def test_07_do_consume_with_partial_quantities(self):
        """Test consuming with partial quantities."""
        # create and confirm production
        production = self.env["mrp.production"].create(
            {
                "product_id": self.product.id,
                "product_qty": 1,
                "bom_id": self.bom.id,
            }
        )
        production.action_confirm()
        # create consume wizard
        consume = self.env["mrp.consume"].create(
            {
                "production_id": production.id,
                "product_id": self.product.id,
                "product_uom_id": production.product_uom_id.id,
                "product_qty": 1,
            }
        )
        consume._onchange_product_qty()
        # set quantities to half
        for line in consume.line_ids:
            line.qty_done = line.qty_to_consume / 2
        # execute consume
        result = consume.do_consume()
        # verify success
        self.assertEqual(result["type"], "ir.actions.act_window_close")

    def test_08_action_minimize_qty_done(self):
        """Test action_minimize_qty_done clears all quantities."""
        # create and confirm production
        production = self.env["mrp.production"].create(
            {
                "product_id": self.product.id,
                "product_qty": 1,
                "bom_id": self.bom.id,
            }
        )
        production.action_confirm()
        # create consume wizard
        consume = self.env["mrp.consume"].create(
            {
                "production_id": production.id,
                "product_id": self.product.id,
                "product_uom_id": production.product_uom_id.id,
                "product_qty": 1,
            }
        )
        consume._onchange_product_qty()
        # set all quantities
        for line in consume.line_ids:
            line.qty_done = line.qty_to_consume
        # minimize
        result = consume.action_minimize_qty_done()
        self.assertEqual(result["type"], "ir.actions.act_window")
        # verify all quantities are zero
        self.assertTrue(all(line.qty_done == 0 for line in consume.line_ids))

    def test_09_action_maximize_qty_done_reserved(self):
        """Test action_maximize_qty_done_reserved sets to reserved."""
        # create and confirm production
        production = self.env["mrp.production"].create(
            {
                "product_id": self.product.id,
                "product_qty": 1,
                "bom_id": self.bom.id,
            }
        )
        production.action_confirm()
        # create consume wizard
        consume = self.env["mrp.consume"].create(
            {
                "production_id": production.id,
                "product_id": self.product.id,
                "product_uom_id": production.product_uom_id.id,
                "product_qty": 1,
            }
        )
        consume._onchange_product_qty()
        # maximize to reserved
        result = consume.action_maximize_qty_done_reserved()
        self.assertEqual(result["type"], "ir.actions.act_window")
        # verify quantities match reserved
        for line in consume.line_ids:
            self.assertEqual(line.qty_done, line.qty_reserved)

    def test_10_action_maximize_qty_done_to_consume(self):
        """Test action_maximize_qty_done_to_consume sets to required."""
        # create and confirm production
        production = self.env["mrp.production"].create(
            {
                "product_id": self.product.id,
                "product_qty": 1,
                "bom_id": self.bom.id,
            }
        )
        production.action_confirm()
        # create consume wizard
        consume = self.env["mrp.consume"].create(
            {
                "production_id": production.id,
                "product_id": self.product.id,
                "product_uom_id": production.product_uom_id.id,
                "product_qty": 1,
            }
        )
        consume._onchange_product_qty()
        # maximize to consume
        result = consume.action_maximize_qty_done_to_consume()
        self.assertEqual(result["type"], "ir.actions.act_window")
        # verify quantities match to_consume
        for line in consume.line_ids:
            self.assertEqual(line.qty_done, line.qty_to_consume)

    def test_11_action_remove_make_to_order(self):
        """Test removing make-to-order lines from consumption."""
        # create and confirm production
        production = self.env["mrp.production"].create(
            {
                "product_id": self.product.id,
                "product_qty": 1,
                "bom_id": self.bom.id,
            }
        )
        production.action_confirm()
        # update one move to make-to-order
        production.move_raw_ids.filtered(
            lambda m: m.product_id == self.raw_material_make_to_order
        ).procure_method = "make_to_order"
        # create consume wizard
        consume = self.env["mrp.consume"].create(
            {
                "production_id": production.id,
                "product_id": self.product.id,
                "product_uom_id": production.product_uom_id.id,
                "product_qty": 1,
            }
        )
        consume._onchange_product_qty()
        initial_count = len(consume.line_ids)
        # remove MTO moves
        result = consume.action_remove_make_to_order()
        self.assertEqual(result["type"], "ir.actions.act_window")
        # verify one line was removed
        self.assertEqual(len(consume.line_ids), initial_count - 1)

    def test_12_reopen_action(self):
        """Test _reopen returns correct action."""
        # create consume wizard
        consume = self.env["mrp.consume"].create({})
        # call reopen
        result = consume._reopen()
        # verify action details
        self.assertEqual(result["type"], "ir.actions.act_window")
        self.assertEqual(result["view_mode"], "form")
        self.assertEqual(result["res_id"], consume.id)
        self.assertEqual(result["res_model"], "mrp.consume")
        self.assertEqual(result["target"], "new")
