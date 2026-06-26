# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, May 2023

import logging

from odoo.exceptions import UserError
from odoo.tools.float_utils import float_compare

from .common import TestPurchaseMergeCommon

_logger = logging.getLogger(__name__)


class TestPurchaseMerge(TestPurchaseMergeCommon):
    """Tests for purchase_merge module."""

    def test_01_order_merge_same_partners(self):
        """Merge two orders from the same partner and check that both are cancelled."""
        ctx = {
            "active_model": self.purchase_model._name,
            "active_ids": (self.order_1 + self.order_2).ids,
        }
        wizard_id = self.merge_order_wizard_model.with_context(**ctx).create({})
        wizard_id.action_merge()
        self.assertEqual(self.order_1.state, "cancel")
        self.assertEqual(len(self.order_1.order_line), 0)
        self.assertEqual(self.order_2.state, "cancel")
        self.assertEqual(len(self.order_2.order_line), 0)
        self.assertEqual(wizard_id.order_id.state, "draft")

    def test_02_order_merge_incompatible_states_cancelled(self):
        """Raise an error when one of the selected orders is cancelled."""
        self.order_1.button_cancel()
        ctx = {
            "active_model": self.purchase_model._name,
            "active_ids": (self.order_1 + self.order_2).ids,
        }
        with (
            self.assertRaisesRegex(UserError, r"incompatible states"),
            self.env.cr.savepoint(),
        ):
            wizard_id = self.merge_order_wizard_model.with_context(**ctx).create({})
            wizard_id.action_merge()

    def test_03_order_merge_incompatible_states_confirmed(self):
        """Raise an error when one of the selected orders is confirmed."""
        self.order_1.button_confirm()
        ctx = {
            "active_model": self.purchase_model._name,
            "active_ids": (self.order_1 + self.order_2).ids,
        }
        with (
            self.assertRaisesRegex(UserError, r"incompatible states"),
            self.env.cr.savepoint(),
        ):
            wizard_id = self.merge_order_wizard_model.with_context(**ctx).create({})
            wizard_id.action_merge()

    def test_04_order_merge_different_partners(self):
        """Raise an error when the selected orders have different suppliers."""
        ctx = {
            "active_model": self.purchase_model._name,
            "active_ids": (self.order_1 + self.order_3).ids,
        }
        with (
            self.assertRaisesRegex(
                UserError, r"All orders must have the same supplier"
            ),
            self.env.cr.savepoint(),
        ):
            wizard_id = self.merge_order_wizard_model.with_context(**ctx).create({})
            wizard_id.action_merge()

    def test_05_order_merge_quantities(self):
        """Merge two orders with shared product and check quantity aggregation."""
        self.assertEqual(
            self.order_1.order_line[0].product_id,
            self.order_2.order_line[0].product_id,
        )
        line_1_product_id = self.order_1.order_line[0].product_id
        line_1_order_1_qty = self.order_1.order_line[0].product_qty
        line_1_order_2_qty = self.order_2.order_line[0].product_qty
        wizard_id = self.merge_order_wizard_model.with_context(
            active_model=self.purchase_model._name,
            active_ids=(self.order_1 + self.order_2).ids,
        ).create({})
        wizard_id.merge_quantities = True
        wizard_id.action_merge()
        self.assertEqual(self.order_1.state, "cancel")
        self.assertEqual(len(self.order_1.order_line), 0)
        self.assertEqual(self.order_2.state, "cancel")
        self.assertEqual(len(self.order_2.order_line), 0)
        self.assertEqual(wizard_id.order_id.state, "draft")
        self.assertEqual(
            wizard_id.order_id.order_line[0].product_id,
            line_1_product_id,
        )
        dp = self.env["decimal.precision"].precision_get("Product Unit of Measure")
        qty_a = wizard_id.order_id.order_line[0].product_qty
        qty_b = line_1_order_1_qty + line_1_order_2_qty
        _logger.info(
            "Merged order line quantity: %s, expected quantity: %s", qty_a, qty_b
        )
        self.assertTrue(float_compare(qty_a, qty_b, precision_digits=dp) == 0)

    def test_06_order_delete_remaining_orders(self):
        """Delete remaining orders after merge when post_process is 'delete'."""
        ctx = {
            "active_model": self.purchase_model._name,
            "active_ids": (self.order_1 + self.order_2).ids,
        }
        wizard_id = self.merge_order_wizard_model.with_context(**ctx).create({})
        wizard_id.post_process = "delete"
        wizard_id.action_merge()
        self.assertFalse(self.order_1.exists())
        self.assertFalse(self.order_2.exists())
