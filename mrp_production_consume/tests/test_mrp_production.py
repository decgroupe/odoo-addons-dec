# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by GitHub Copilot <copilot at github.com>, Mar 2026

from .common import TestMrpConsumeBase


class TestMrpProductionConsume(TestMrpConsumeBase):
    """Test cases for MRP Production consume functionality."""

    def _consume_moves(self, move_ids):
        for move in move_ids.filtered(lambda m: m.state not in ("done", "cancel")):
            move.quantity = move.product_uom_qty
            move.picked = True

    @classmethod
    def setUpClass(cls):
        """Set up test data."""
        super().setUpClass()
        # # Create a simple product
        # cls.product = cls.env["product.product"].create({
        #     "name": "Test Product",
        #     "type": "consu",
        #     "is_storable": True,
        # })
        # # Create raw materials
        # cls.raw_material_1 = cls.env["product.product"].create({
        #     "name": "Raw Material 1",
        #     "type": "consu",
        #     "is_storable": True,
        # })
        # cls.raw_material_2 = cls.env["product.product"].create({
        #     "name": "Raw Material 2",
        #     "type": "consu",
        #     "is_storable": True,
        # })
        # # Create a warehouse
        # cls.warehouse = cls.env["stock.warehouse"].search([], limit=1)
        # cls.location = cls.warehouse.lot_stock_id
        # # Create a BOM
        # cls.bom = cls.env["mrp.bom"].create({
        #     "product_id": cls.product.id,
        #     "product_tmpl_id": cls.product.product_tmpl_id.id,
        #     "product_qty": 1,
        #     "type": "normal",
        #     "bom_line_ids": [
        #         Command.create({
        #             "product_id": cls.raw_material_1.id,
        #             "product_qty": 2,
        #         }),
        #         Command.create({
        #             "product_id": cls.raw_material_2.id,
        #             "product_qty": 1,
        #         }),
        #     ],
        # })

    def test_01_post_inventory_consume_basic(self):
        """Test basic _post_inventory_consume functionality."""
        # Create production order
        production = self.env["mrp.production"].create(
            {
                "product_id": self.product.id,
                "product_qty": 1,
                "bom_id": self.bom.id,
            }
        )
        # Confirm production
        production.action_confirm()
        self.assertEqual(production.state, "confirmed")
        # Get raw material moves
        raw_moves = production.move_raw_ids.filtered(
            lambda m: m.state not in ("done", "cancel")
        )
        self.assertEqual(len(raw_moves), 3)
        # Execute consume with first material only
        first_move = raw_moves[0:1]
        self._consume_moves(first_move)
        result = production._post_inventory_consume(first_move)
        self.assertTrue(result)
        # Verify move is done
        self.assertEqual(first_move.state, "done")

    def test_02_post_inventory_consume_multiple_moves(self):
        """Test consuming multiple raw material moves at once."""
        # Create production order
        production = self.env["mrp.production"].create(
            {
                "product_id": self.product.id,
                "product_qty": 1,
                "bom_id": self.bom.id,
            }
        )
        production.action_confirm()
        raw_moves = production.move_raw_ids.filtered(
            lambda m: m.state not in ("done", "cancel")
        )
        self.assertEqual(len(raw_moves), 3)
        # Consume all moves
        self._consume_moves(raw_moves)
        result = production._post_inventory_consume(raw_moves)
        self.assertTrue(result)
        # Verify all moves are done
        self.assertTrue(all(move.state == "done" for move in raw_moves))

    def test_03_post_inventory_links_consume_lines(self):
        """Test that consumed lines are linked to finished product."""
        # Create production order
        production = self.env["mrp.production"].create(
            {
                "product_id": self.product.id,
                "product_qty": 1,
                "bom_id": self.bom.id,
            }
        )
        production.action_confirm()
        raw_moves = production.move_raw_ids.filtered(
            lambda m: m.state not in ("done", "cancel")
        )
        # Consume moves
        self._consume_moves(raw_moves)
        production._post_inventory_consume(raw_moves)
        # Get finished product move line
        finish_move_lines = production.move_finished_ids.mapped("move_line_ids")
        self.assertTrue(len(finish_move_lines) > 0)
        # Verify consume lines are linked
        for finish_line in finish_move_lines:
            self.assertTrue(len(finish_line.consume_line_ids) > 0)

    def test_04_post_inventory_ignores_done_moves(self):
        """Test that already done moves are ignored in _post_inventory_consume."""
        # Create production order
        production = self.env["mrp.production"].create(
            {
                "product_id": self.product.id,
                "product_qty": 1,
                "bom_id": self.bom.id,
            }
        )
        production.action_confirm()
        raw_moves = production.move_raw_ids.filtered(
            lambda m: m.state not in ("done", "cancel")
        )
        # Manually mark first move as done
        raw_moves[0].state = "done"
        # Consume all moves
        self._consume_moves(raw_moves)
        production._post_inventory_consume(raw_moves)
        # Verify first move is still done and second is done
        self.assertEqual(raw_moves[0].state, "done")
        self.assertEqual(raw_moves[1].state, "done")

    def test_05_post_inventory_with_cancel_backorder(self):
        """Test _post_inventory_consume with cancel_backorder parameter."""
        # Create production order
        production = self.env["mrp.production"].create(
            {
                "product_id": self.product.id,
                "product_qty": 1,
                "bom_id": self.bom.id,
            }
        )
        production.action_confirm()
        raw_moves = production.move_raw_ids.filtered(
            lambda m: m.state not in ("done", "cancel")
        )
        # Consume with cancel_backorder=True
        self._consume_moves(raw_moves)
        result = production._post_inventory_consume(raw_moves, cancel_backorder=True)
        self.assertTrue(result)
        # Verify moves are done
        self.assertTrue(all(move.state == "done" for move in raw_moves))

    def test_06_open_consume_action(self):
        """Test opening consume wizard action."""
        # Create and confirm production
        production = self.env["mrp.production"].create(
            {
                "product_id": self.product.id,
                "product_qty": 1,
                "bom_id": self.bom.id,
            }
        )
        production.action_confirm()
        # Open consume action
        result = production.open_consume()
        # Verify action details
        self.assertEqual(result["type"], "ir.actions.act_window")
        self.assertIn("mrp.consume", result.get("res_model", ""))

    def test_07_post_inventory_preserves_consume_lines(self):
        """Test that _post_inventory preserves consume_move_lines."""
        # Create production order
        production = self.env["mrp.production"].create(
            {
                "product_id": self.product.id,
                "product_qty": 1,
                "bom_id": self.bom.id,
            }
        )
        production.action_confirm()
        raw_moves = production.move_raw_ids.filtered(
            lambda m: m.state not in ("done", "cancel")
        )
        # First consume some moves
        self._consume_moves(raw_moves[0:1])
        production._post_inventory_consume(raw_moves[0:1])
        # Save the initial consume lines
        initial_consume_lines = production.move_finished_ids.mapped(
            "move_line_ids.consume_line_ids"
        )
        self.assertEqual(len(initial_consume_lines), 1)
        # Now call full _post_inventory
        production.button_mark_done()
        # Verify consume lines are still there
        final_consume_lines = production.move_finished_ids.mapped(
            "move_line_ids.consume_line_ids"
        )
        self.assertEqual(len(final_consume_lines), 3)
        self.assertIn(initial_consume_lines, final_consume_lines)

    def test_08_post_inventory_empty_moves(self):
        """Test _post_inventory_consume with empty move set."""
        # Create production order
        production = self.env["mrp.production"].create(
            {
                "product_id": self.product.id,
                "product_qty": 1,
                "bom_id": self.bom.id,
            }
        )
        production.action_confirm()
        # Create empty move set
        empty_moves = self.env["stock.move"]
        # Consume empty set should not raise error
        result = production._post_inventory_consume(empty_moves)
        self.assertTrue(result)
