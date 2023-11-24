# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Apr 2023

from odoo.addons.stock_actions.tests.common import TestStockActionCommon
from odoo.exceptions import UserError
from odoo.tests import new_test_user
from odoo.tests.common import SavepointCase


class TestStockAction(TestStockActionCommon):
    """ """

    @classmethod
    def setUpClass(cls):
        super().setUpClass()

    def setUp(self):
        super(TestStockAction, self).setUp()

    def test_01_validate_stock_move_reassignable_states(self):
        """Tests that all hard-coded states match existing ones"""
        state_field = self.MoveObj._fields["state"]
        sm_states = [s[0] for s in state_field.selection]
        for state in self.MoveObj._get_reassignable_states():
            self.assertIn(state, sm_states)

    def test_02_basic_move(self):
        customer_move = self._send_to_customer(self.product, 5.0)

        self.assertEqual(customer_move.product_uom, self.product.uom_id)
        self.assertEqual(customer_move.location_id, self.warehouse_1.lot_stock_id)
        self.assertEqual(customer_move.location_dest_id, self.customer_location)

        self.assertEqual(customer_move.state, "draft")
        self.assertEqual(customer_move.is_cancellable, True)
        self.assertEqual(customer_move.action_reassign_visible, False)

        customer_move.action_confirm()
        self.assertEqual(customer_move.state, "confirmed")
        self.assertEqual(self.product.qty_available, 0.0)
        self.assertEqual(self.product.virtual_available, -5.0)

        # try to reserve quantity
        customer_move.action_assign()
        # but since quantity is not enough, the state should stay `confirmed`
        self.assertEqual(customer_move.state, "confirmed")

        # receive 2x products from supplier
        self._receive_from_supplier(self.product, 2.0)

        self.product._compute_quantities()
        # physical stock quantity
        self.assertEqual(self.product.qty_available, 2.0)
        # unreserved stock quantity
        self.assertEqual(self.product.virtual_available, -3.0)

        # retry to reserve quantity
        customer_move.action_assign()
        # only 2/5 should be available
        self.assertEqual(customer_move.state, "partially_available")

        # receive 3x products from supplier
        self._receive_from_supplier(self.product, 3.0)

        self.product._compute_quantities()
        # physical stock quantity
        self.assertEqual(self.product.qty_available, 5.0)
        # unreserved stock quantity
        self.assertEqual(self.product.virtual_available, 0.0)

        # retry to reserve quantity
        customer_move.action_assign()
        # all 5/5 should be available
        self.assertEqual(customer_move.state, "assigned")

        # try the reassign action (unreserve all and re-assign)
        customer_move.action_reassign()
        # all 5/5 should be available
        self.assertEqual(customer_move.state, "assigned")

    def _create_linked_moves(self, product, product_uom_qty, confirm=True):
        move_stock_pack = self._create_move(
            product=product,
            src_location=self.stock_location,
            dst_location=self.pack_location,
            product_uom_qty=product_uom_qty,
            name="test_link_assign_1_1",
        )
        move_pack_cust = self._create_move(
            product=product,
            src_location=self.pack_location,
            dst_location=self.customer_location,
            product_uom_qty=product_uom_qty,
            name="test_link_assign_1_2",
        )
        move_stock_pack.write({"move_dest_ids": [(4, move_pack_cust.id, 0)]})
        self.assertEqual(move_pack_cust.move_orig_ids, move_stock_pack)
        if confirm:
            (move_stock_pack + move_pack_cust)._action_confirm()
            self.assertEqual(move_stock_pack.state, "confirmed")
            self.assertEqual(move_pack_cust.state, "waiting")

        return move_stock_pack, move_pack_cust

    def test_03_linked_moves_cancel_first_one(self):
        # create linked moves (stock --> packing --> customer)
        move_stock_pack, move_pack_cust = self._create_linked_moves(self.product, 1.0)
        # cancel initial move
        move_stock_pack.action_cancel()
        self.assertEqual(move_stock_pack.state, "cancel")
        self.assertEqual(move_pack_cust.state, "cancel")

    def test_04_linked_moves_cancel_second_one(self):
        # create linked moves (stock --> packing --> customer)
        move_stock_pack, move_pack_cust = self._create_linked_moves(self.product, 1.0)
        # cancel last move
        move_pack_cust.action_cancel()
        self.assertEqual(move_stock_pack.state, "confirmed")
        self.assertEqual(move_pack_cust.state, "cancel")

    def test_05_linked_moves_cancel_downstream_first_one(self):
        # create linked moves (stock --> packing --> customer)
        move_stock_pack, move_pack_cust = self._create_linked_moves(self.product, 1.0)
        # cancel last move
        move_stock_pack.action_cancel_downstream()
        self.assertEqual(move_stock_pack.state, "cancel")
        self.assertEqual(move_pack_cust.state, "cancel")

    def test_06_linked_moves_cancel_upstream_second_one(self):
        # create linked moves (stock --> packing --> customer)
        move_stock_pack, move_pack_cust = self._create_linked_moves(self.product, 1.0)
        # cancel last move
        move_pack_cust.action_cancel_upstream()
        self.assertEqual(move_stock_pack.state, "cancel")
        self.assertEqual(move_pack_cust.state, "cancel")
