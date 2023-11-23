# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, May 2023

from odoo.tests.common import TransactionCase
from odoo.exceptions import UserError
from odoo.tools.float_utils import float_compare


class TestPurchaseMerge(TransactionCase):
    """ """

    def setUp(self):
        super().setUp()
        self.purchase_model = self.env["purchase.order"]
        self.purchase_line_model = self.env["purchase.order.line"]
        self.procurement_group_model = self.env["procurement.group"]
        self.merge_order_wizard_model = self.env["purchase.order.merge"]
        self.order_1 = self.env.ref("purchase_merge.purchase_order_1")
        self.order_2 = self.env.ref("purchase_merge.purchase_order_2")
        self.assertEqual(self.order_1.partner_id, self.order_2.partner_id)
        self.order_3 = self.env.ref("purchase_merge.purchase_order_3")
        self.assertNotEqual(self.order_1.partner_id, self.order_3.partner_id)
        self.assertNotEqual(self.order_2.partner_id, self.order_3.partner_id)

    def test_01_order_merge_same_partners(self):
        ctx = {
            "active_model": self.purchase_model._name,
            "active_ids": (self.order_1 + self.order_2).ids,
        }
        wizard_id = self.merge_order_wizard_model.with_context(ctx).create({})
        wizard_id.action_merge()
        self.assertEqual(self.order_1.state, "cancel")
        self.assertEqual(len(self.order_1.order_line), 0)
        self.assertEqual(self.order_2.state, "cancel")
        self.assertEqual(len(self.order_2.order_line), 0)
        self.assertEqual(wizard_id.order_id.state, "draft")

    def test_02_order_merge_incompatible_states(self):
        self.order_1.button_cancel()
        ctx = {
            "active_model": self.purchase_model._name,
            "active_ids": (self.order_1 + self.order_2).ids,
        }
        with self.assertRaisesRegex(
            UserError, r"incompatible states"
        ), self.cr.savepoint():
            wizard_id = self.merge_order_wizard_model.with_context(ctx).create({})
            wizard_id.action_merge()

    def test_03_order_merge_incompatible_states(self):
        self.order_1.button_confirm()
        ctx = {
            "active_model": self.purchase_model._name,
            "active_ids": (self.order_1 + self.order_2).ids,
        }
        with self.assertRaisesRegex(
            UserError, r"incompatible states"
        ), self.cr.savepoint():
            wizard_id = self.merge_order_wizard_model.with_context(ctx).create({})
            wizard_id.action_merge()

    def test_04_order_merge_different_partners(self):
        ctx = {
            "active_model": self.purchase_model._name,
            "active_ids": (self.order_1 + self.order_3).ids,
        }
        with self.assertRaisesRegex(
            UserError, r"All orders must have the same supplier"
        ), self.cr.savepoint():
            wizard_id = self.merge_order_wizard_model.with_context(ctx).create({})
            wizard_id.action_merge()

    def test_04_order_merge_quantities(self):
        self.assertEqual(
            self.order_1.order_line[0].product_id,
            self.order_2.order_line[0].product_id,
        )
        line_1_product_id = self.order_1.order_line[0].product_id
        line_1_order_1_subtotal = self.order_1.order_line[0].price_subtotal
        line_1_order_2_subtotal = self.order_2.order_line[0].price_subtotal
        ctx = {
            "active_model": self.purchase_model._name,
            "active_ids": (self.order_1 + self.order_2).ids,
        }
        wizard_id = self.merge_order_wizard_model.with_context(ctx).create({})
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
        dp = self.env["decimal.precision"].precision_get("Product Price")
        self.assertTrue(
            float_compare(
                wizard_id.order_id.order_line[0].price_subtotal,
                line_1_order_1_subtotal + line_1_order_2_subtotal,
                precision_digits=dp,
            )
            == 0
        )

    def test_05_order_delete_remaining_orders(self):
        ctx = {
            "active_model": self.purchase_model._name,
            "active_ids": (self.order_1 + self.order_2).ids,
        }
        wizard_id = self.merge_order_wizard_model.with_context(ctx).create({})
        wizard_id.post_process = "delete"
        wizard_id.action_merge()
        self.assertFalse(self.order_1.exists())
        self.assertFalse(self.order_2.exists())
