# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Oct 2023

from odoo.tests.common import TransactionCase


class TestAccountSaleLink(TransactionCase):
    def setUp(self):
        super().setUp()

    def _confirm_sale_order(self, so):
        so.action_confirm()
        for line in so.order_line:
            line.qty_delivered = line.product_uom_qty
        invoice_id = so._create_invoices()
        self.env["account.move"].invalidate_cache()
        return invoice_id

    def test_01_link(self):
        so = self.env.ref("sale.sale_order_3")
        invoice_id = self._confirm_sale_order(so)
        self.assertTrue(invoice_id.exists())
        self.assertEqual(len(invoice_id.sale_order_ids), 1)
        self.assertEqual(invoice_id.sale_order_count, 1)
        self.assertEqual(invoice_id.sale_order_ids.id, so.id)

    def test_02_view(self):
        so = self.env.ref("sale.sale_order_2")
        invoice_id = self._confirm_sale_order(so)
        self.assertTrue(invoice_id.exists())
        action_view_sale_order = invoice_id.action_view_sale_order()
        self.assertEqual(action_view_sale_order["type"], "ir.actions.act_window")
        self.assertEqual(action_view_sale_order["res_id"], so.id)
