# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Jan 2026

from odoo.tests.common import TransactionCase

from ..models.stock_move import LIST_COLORS


class TestStockPickingColored(TransactionCase):
    """Test stock move list colors computation based on procurement group."""

    def _create_move(self, group=None):
        """Helper to create a stock move with optional procurement group."""
        return self.env["stock.move"].create(
            {
                "name": "Test Move",
                "product_id": self.product.id,
                "product_uom_qty": 1.0,
                "product_uom": self.product.uom_id.id,
                "location_id": self.stock_location.id,
                "location_dest_id": self.customer_location.id,
                "group_id": group.id if group else False,
            }
        )

    def _create_group(self, name):
        """Helper to create a procurement group."""
        return self.env["procurement.group"].create({"name": name})

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.stock_location = cls.env.ref("stock.stock_location_stock")
        cls.customer_location = cls.env.ref("stock.stock_location_customers")
        cls.product = cls.env["product.product"].create(
            {
                "name": "Test Product",
                "type": "consu",
                "is_storable": True,
            }
        )

    def test_01_single_move_no_color(self):
        """A single move should not have colors assigned."""
        move = self._create_move()
        self.assertFalse(move.list_bg_color)
        self.assertFalse(move.list_fg_color)

    def test_02_single_group_no_color(self):
        """Moves with a single group should not have colors assigned."""
        group = self._create_group("Group A")
        move1 = self._create_move(group)
        move2 = self._create_move(group)
        moves = move1 | move2
        moves._compute_list_colors()
        for move in moves:
            self.assertFalse(move.list_bg_color)
            self.assertFalse(move.list_fg_color)

    def test_03_multiple_groups_have_colors(self):
        """Moves with different groups should have different colors."""
        group_a = self._create_group("Group A")
        group_b = self._create_group("Group B")
        move1 = self._create_move(group_a)
        move2 = self._create_move(group_b)
        moves = move1 | move2
        moves._compute_list_colors()
        # both moves should have colors
        self.assertTrue(move1.list_bg_color)
        self.assertTrue(move1.list_fg_color)
        self.assertTrue(move2.list_bg_color)
        self.assertTrue(move2.list_fg_color)
        # colors should be different for different groups
        self.assertNotEqual(move1.list_bg_color, move2.list_bg_color)

    def test_04_same_group_same_color(self):
        """Moves with the same group should have the same color."""
        group_a = self._create_group("Group A")
        group_b = self._create_group("Group B")
        move1 = self._create_move(group_a)
        move2 = self._create_move(group_a)
        move3 = self._create_move(group_b)
        moves = move1 | move2 | move3
        moves._compute_list_colors()
        # moves in the same group should have the same color
        self.assertEqual(move1.list_bg_color, move2.list_bg_color)
        self.assertEqual(move1.list_fg_color, move2.list_fg_color)
        # moves in different groups should have different colors
        self.assertNotEqual(move1.list_bg_color, move3.list_bg_color)

    def test_05_color_cycle_with_modulo(self):
        """Colors should cycle when there are more groups than available colors."""
        # create more groups than available colors
        groups = [self._create_group(f"Group {i}") for i in range(len(LIST_COLORS) + 2)]
        moves = self.env["stock.move"]
        for group in groups:
            moves |= self._create_move(group)
        moves._compute_list_colors()
        # all moves should have colors (no blank fallback)
        for move in moves:
            self.assertTrue(move.list_bg_color)
            self.assertTrue(move.list_fg_color)

    def test_06_move_without_group_in_mixed_set(self):
        """Moves without a group should not get colors even in a mixed set."""
        group_a = self._create_group("Group A")
        move_with_group = self._create_move(group_a)
        move_without_group = self._create_move()
        moves = move_with_group | move_without_group
        moves._compute_list_colors()
        # move with group should have a color
        self.assertTrue(move_with_group.list_bg_color)
        # move without group should not have a color
        self.assertFalse(move_without_group.list_bg_color)
