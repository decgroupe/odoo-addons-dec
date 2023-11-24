# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Nov 2023

from odoo.addons.stock_actions.tests.common import TestStockActionCommon
from odoo.exceptions import UserError
from odoo.tests import new_test_user


class TestPurchaseStockCancel(TestStockActionCommon):
    """ """

    def setUp(self):
        super().setUp()
        self.purchase_model = self.env["purchase.order"]
        self.purchase_line_model = self.env["purchase.order.line"]
        # User
        ctx = {
            "mail_create_nolog": True,
            "mail_create_nosubscribe": True,
            "mail_notrack": True,
            "no_reset_password": True,
        }
        self.purchase_manager = new_test_user(
            self.env,
            login="purchase_stock_cancel-user",
            groups="purchase.group_purchase_manager",
            context=ctx,
        )
        # [FURN_1118] Corner Desk Left Sit
        self.product13 = self.env.ref("product.product_product_13")
        self.product13.route_ids += self.route_mto

    def test_01_check_existing_demo_data(self):
        """Check that existing demo data is still not enough to test this module and
        `purchase_stock_cancel_tests` is still needed"""
        orders = self.purchase_model.search([])
        for po in orders:
            for line in po.order_line:
                self.assertFalse(line.move_dest_ids)

    def test_02_propagate_cancel_on_validated_po(self):
        order = self.env.ref("purchase_stock.purchase_order_8")
        self.assertEqual(order.state, "purchase")
        self.assertEqual(len(order.order_line), 1)
        line1 = order.order_line[0]
        exception_regex = (
            r"Cannot delete a purchase order line which is in state 'purchase'."
        )
        with self.assertRaisesRegex(UserError, exception_regex), self.cr.savepoint():
            line1.with_context(propagate=True).action_propagate_cancel()
        with self.assertRaisesRegex(UserError, exception_regex), self.cr.savepoint():
            line1.with_context(propagate=False).action_propagate_cancel()

    def test_03_propagate_cancel_on_quotation(self):
        order = self.env.ref("purchase.purchase_order_6")
        self.assertEqual(order.state, "draft")
        self.assertEqual(len(order.order_line), 3)
        line1 = order.order_line[0]
        line2 = order.order_line[1]
        line3 = order.order_line[2]
        line1.with_context(propagate=True).action_propagate_cancel()
        self.assertFalse(line1.exists())
        self.assertEqual(order.state, "draft")
        line2.with_context(propagate=False).action_propagate_cancel()
        self.assertFalse(line2.exists())
        self.assertEqual(order.state, "draft")
        line3.with_context(propagate=False).action_propagate_cancel()
        self.assertFalse(line3.exists())
        self.assertEqual(order.state, "cancel")

    def test_04_create_po_from_picking_then_cancel_with_propagation(self):
        customer_move = self._send_to_customer(self.product13, 5.0)
        customer_move.procure_method = "make_to_order"
        self.assertEqual(customer_move.state, "draft")
        picking_id = customer_move.picking_id
        picking_id.action_confirm()
        self.assertEqual(customer_move.state, "waiting")
        line = customer_move.created_purchase_line_id
        self.assertTrue(line.exists())
        # Use the dedicated purchase user for this action
        line.with_user(self.purchase_manager).with_context(
            propagate=True
        ).action_propagate_cancel()
        self.assertFalse(line.exists())
        self.assertEqual(customer_move.state, "cancel")

    def test_05_create_po_from_picking_then_cancel_without_propagation(self):
        customer_move = self._send_to_customer(self.product13, 5.0)
        customer_move.procure_method = "make_to_order"
        self.assertEqual(customer_move.state, "draft")
        picking_id = customer_move.picking_id
        picking_id.action_confirm()
        self.assertEqual(customer_move.state, "waiting")
        line = customer_move.created_purchase_line_id
        self.assertTrue(line.exists())
        # Use the dedicated purchase user for this action
        line.with_user(self.purchase_manager).with_context(
            propagate=False
        ).action_propagate_cancel()
        self.assertFalse(line.exists())
        self.assertEqual(customer_move.state, "confirmed")
