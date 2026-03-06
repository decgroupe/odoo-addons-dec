# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by GitHub Copilot <copilot at github.com>, Mar 2026

from .common import TestMrpConsumeBase


class TestMrpConsumeLine(TestMrpConsumeBase):
    """Test cases for MRP Consume Line model."""

    @classmethod
    def setUpClass(cls):
        """Set up test data."""
        super().setUpClass()

    def test_01_consume_line_creation(self):
        """Test creating a consume line."""
        # create production
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
        # verify lines exists
        self.assertEqual(len(consume.line_ids), 3)
        line1 = consume.line_ids[0]
        self.assertEqual(line1.product_id, self.raw_material_1)
        self.assertEqual(line1.qty_to_consume, 2)
        line2 = consume.line_ids[1]
        self.assertEqual(line2.product_id, self.raw_material_2)
        self.assertEqual(line2.qty_to_consume, 1)
        line3 = consume.line_ids[2]
        self.assertEqual(line3.product_id, self.raw_material_make_to_order)
        self.assertEqual(line3.qty_to_consume, 1)

    def test_02_consume_line_onchange_product_id(self):
        """Test _onchange_product_id sets correct UoM."""
        # create a consume line
        line = self.env["mrp.consume.line"].create(
            {
                "product_id": self.raw_material_1.id,
                "qty_to_consume": 1,
            }
        )
        # trigger onchange
        line._onchange_product_id()
        # verify UoM is set
        self.assertEqual(line.product_uom_id, self.raw_material_1.uom_id)

    def test_03_consume_line_is_minimized(self):
        """Test is_minimized computation."""
        # create consume line with qty_done = 0
        line = self.env["mrp.consume.line"].create(
            {
                "product_id": self.raw_material_1.id,
                "qty_to_consume": 2,
                "qty_reserved": 2,
                "qty_done": 0,
            }
        )
        # verify is_minimized is True
        self.assertTrue(line.is_minimized)

    def test_04_consume_line_is_not_minimized(self):
        """Test is_minimized is False when qty_done > 0."""
        # create consume line with qty_done > 0
        line = self.env["mrp.consume.line"].create(
            {
                "product_id": self.raw_material_1.id,
                "qty_to_consume": 2,
                "qty_reserved": 2,
                "qty_done": 1,
            }
        )
        # verify is_minimized is False
        self.assertFalse(line.is_minimized)

    def test_05_consume_line_is_maximized_reserved(self):
        """Test is_maximized is True when qty_done equals qty_reserved."""
        # create consume line where qty_done = qty_reserved
        line = self.env["mrp.consume.line"].create(
            {
                "product_id": self.raw_material_1.id,
                "qty_to_consume": 2,
                "qty_reserved": 2,
                "qty_done": 2,
            }
        )
        # verify is_maximized is True
        self.assertTrue(line.is_maximized)

    def test_06_consume_line_is_maximized_to_consume(self):
        """Test is_maximized is True when qty_done equals qty_to_consume."""
        # create consume line where qty_done = qty_to_consume
        line = self.env["mrp.consume.line"].create(
            {
                "product_id": self.raw_material_1.id,
                "qty_to_consume": 2,
                "qty_reserved": 3,
                "qty_done": 2,
            }
        )
        # verify is_maximized is True
        self.assertTrue(line.is_maximized)

    def test_07_consume_line_is_not_maximized(self):
        """Test is_maximized is False for intermediate values."""
        # create consume line with intermediate qty_done
        line = self.env["mrp.consume.line"].create(
            {
                "product_id": self.raw_material_1.id,
                "qty_to_consume": 2,
                "qty_reserved": 2,
                "qty_done": 1,
            }
        )
        # verify is_maximized is False
        self.assertFalse(line.is_maximized)

    def test_08_action_minimize_qty_done(self):
        """Test action_minimize_qty_done for line."""
        # create production
        production = self.env["mrp.production"].create(
            {
                "product_id": self.product.id,
                "product_qty": 1,
                "bom_id": self.bom.id,
            }
        )
        production.action_confirm()
        # create consume and line
        consume = self.env["mrp.consume"].create(
            {
                "production_id": production.id,
                "product_id": self.product.id,
                "product_uom_id": production.product_uom_id.id,
                "product_qty": 1,
            }
        )
        consume._onchange_product_qty()
        line = consume.line_ids[0]
        # set quantity
        line.qty_done = 2
        # minimize
        result = line.action_minimize_qty_done()
        # when no consume_id, should return True
        self.assertTrue(result)
        # verify qty_done is reset
        self.assertEqual(line.qty_done, 0)

    def test_09_action_maximize_qty_done_reserved(self):
        """Test action_maximize_qty_done_reserved for line."""
        # create production
        production = self.env["mrp.production"].create(
            {
                "product_id": self.product.id,
                "product_qty": 1,
                "bom_id": self.bom.id,
            }
        )
        production.action_confirm()
        # create consume and line
        consume = self.env["mrp.consume"].create(
            {
                "production_id": production.id,
                "product_id": self.product.id,
                "product_uom_id": production.product_uom_id.id,
                "product_qty": 1,
            }
        )
        consume._onchange_product_qty()
        line = consume.line_ids[0]
        # maximize to reserved
        result = line.action_maximize_qty_done_reserved()
        # when no consume_id, should return True
        self.assertTrue(result)
        # verify qty_done equals qty_reserved
        self.assertEqual(line.qty_done, line.qty_reserved)

    def test_10_consume_line_fields_setup(self):
        """Test that consume line fields are properly set up."""
        # create production
        production = self.env["mrp.production"].create(
            {
                "product_id": self.product.id,
                "product_qty": 1,
                "bom_id": self.bom.id,
            }
        )
        production.action_confirm()
        # create consume and line
        consume = self.env["mrp.consume"].create(
            {
                "production_id": production.id,
                "product_id": self.product.id,
                "product_uom_id": production.product_uom_id.id,
                "product_qty": 1,
            }
        )
        consume._onchange_product_qty()
        line = consume.line_ids[0]
        # verify all fields are set
        self.assertIsNotNone(line.consume_id)
        self.assertIsNotNone(line.product_id)
        self.assertIsNotNone(line.product_uom_id)
        self.assertIsNotNone(line.move_id)
        self.assertGreater(line.qty_to_consume, 0)
        self.assertGreaterEqual(line.qty_reserved, 0)
