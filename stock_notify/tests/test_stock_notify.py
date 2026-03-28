# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Mar 2026

from odoo.tests.common import TransactionCase


class TestStockNotify(TransactionCase):
    """Tests for stock_notify module."""

    @classmethod
    def setUpClass(cls):
        """Set up shared test data."""
        super().setUpClass()
        cls.product = cls.env["product.product"].create(
            {
                "name": "Test Product",
                "type": "consu",
                "is_storable": True,
            }
        )
        cls.location_src = cls.env.ref("stock.stock_location_stock")
        cls.location_dest = cls.env.ref("stock.stock_location_customers")

    def _create_picking_with_move(self, notify_assigned=False):
        """Create a stock picking with one move and return both."""
        picking = self.env["stock.picking"].create(
            {
                "picking_type_id": self.env.ref("stock.picking_type_out").id,
                "location_id": self.location_src.id,
                "location_dest_id": self.location_dest.id,
            }
        )
        move = self.env["stock.move"].create(
            {
                "name": "Test Move",
                "product_id": self.product.id,
                "product_uom_qty": 1,
                "product_uom": self.product.uom_id.id,
                "picking_id": picking.id,
                "location_id": self.location_src.id,
                "location_dest_id": self.location_dest.id,
                "notify_assigned": notify_assigned,
            }
        )
        return picking, move

    def test_01_no_notify_no_message(self):
        """No message posted when notify_assigned is False."""
        picking, move = self._create_picking_with_move(notify_assigned=False)
        msg_count_before = len(picking.message_ids)
        move.write({"state": "assigned"})
        self.assertEqual(len(picking.message_ids), msg_count_before)

    def test_02_notify_posts_message(self):
        """A message is posted on the picking when notify_assigned is True."""
        picking, move = self._create_picking_with_move(notify_assigned=True)
        # first quant to cover availability
        self.env["stock.quant"].create(
            {
                "product_id": self.product.id,
                "location_id": self.location_src.id,
                "quantity": 10,
            }
        )
        msg_count_before = len(picking.message_ids)
        move.write({"state": "assigned"})
        self.assertGreater(len(picking.message_ids), msg_count_before)

    def test_03_message_contains_product_name(self):
        """The posted message body contains the product display name."""
        picking, move = self._create_picking_with_move(notify_assigned=True)
        move.write({"state": "assigned"})
        messages_after = picking.message_ids
        body_texts = [m.body for m in messages_after]
        self.assertTrue(any(self.product.display_name in body for body in body_texts))

    def test_04_no_notify_when_other_state(self):
        """No message posted when state changes to something other than assigned."""
        picking, move = self._create_picking_with_move(notify_assigned=True)
        msg_count_before = len(picking.message_ids)
        move.write({"state": "confirmed"})
        self.assertEqual(len(picking.message_ids), msg_count_before)
