# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Oct 2023

from odoo.tests.common import TransactionCase


class TestAccountPurchaseLink(TransactionCase):
    def setUp(self):
        super().setUp()

    def _confirm_purchase_order(self, po):
        po.button_confirm()
        for line in po.order_line:
            line.qty_received = line.product_qty
        action_view_invoice = po.action_create_invoice()
        self.env["account.move"].invalidate_cache()
        return action_view_invoice

    def test_01_link(self):
        po = self.env.ref("purchase.purchase_order_7")
        action_view_invoice = self._confirm_purchase_order(po)
        invoice_id = self.env["account.move"].browse(action_view_invoice["res_id"])
        self.assertTrue(invoice_id.exists())
        self.assertEqual(len(invoice_id.purchase_order_ids), 1)
        self.assertEqual(invoice_id.purchase_order_count, 1)
        self.assertEqual(invoice_id.purchase_order_ids.id, po.id)

    def test_02_view(self):
        po = self.env.ref("purchase.purchase_order_5")
        action_view_invoice = self._confirm_purchase_order(po)
        invoice_id = self.env["account.move"].browse(action_view_invoice["res_id"])
        self.assertTrue(invoice_id.exists())
        action_view_purchase_order = invoice_id.action_view_purchase_order()
        self.assertEqual(action_view_purchase_order["type"], "ir.actions.act_window")
        self.assertEqual(action_view_purchase_order["res_id"], po.id)
