# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Apr 2026

from lxml import etree

from .common import TestPartnerSaleDatesCommon


class TestPartnerSaleDates(TestPartnerSaleDatesCommon):
    """Tests for partner_sale_dates module."""

    def test_01_last_quotation_date_set(self):
        """last_quotation_date is set when a draft sale order exists."""
        so = self._make_sale_order(state=None)
        self.partner.invalidate_recordset()
        self.assertEqual(
            self.partner.last_quotation_date,
            so.date_order.date(),
        )

    def test_02_last_quotation_date_cleared_after_confirm(self):
        """last_quotation_date is cleared once the order is confirmed."""
        self._make_sale_order(state=None)
        self.partner.invalidate_recordset()
        self.assertTrue(self.partner.last_quotation_date)
        # confirm all draft orders
        self.env["sale.order"].search(
            [("partner_id", "=", self.partner.id), ("state", "in", ("draft", "sent"))]
        ).action_confirm()
        self.partner.invalidate_recordset()
        self.assertFalse(self.partner.last_quotation_date)

    def test_03_last_sale_date_set_after_confirm(self):
        """last_sale_date is set once a sale order is confirmed."""
        self.assertFalse(self.partner.last_sale_date)
        so = self._make_sale_order(state="sale")
        self.partner.invalidate_recordset()
        self.assertEqual(
            self.partner.last_sale_date,
            so.date_order.date(),
        )

    def test_04_shipping_sale_order_count(self):
        """shipping_sale_order_count reflects orders shipped to the partner."""
        self.assertEqual(self.partner.shipping_sale_order_count, 0)
        self._make_sale_order(state="sale")
        self.partner.invalidate_recordset()
        self.assertEqual(self.partner.shipping_sale_order_count, 1)

    def test_05_action_open_shipping_sale_orders(self):
        """action_open_shipping_sale_orders returns an ir.actions.act_window."""
        self._make_sale_order(state="sale")
        action = self.partner.action_open_shipping_sale_orders()
        self.assertEqual(action["type"], "ir.actions.act_window")
        domain_ids = action["domain"][0][2]
        self.assertIn(
            self.partner.shipping_sale_order_ids[:1].id,
            domain_ids,
        )

    def test_06_list_view_fields(self):
        """Check that date fields are present in the combined partner list view arch."""
        view_info = self.env["res.partner"].get_view(view_type="list")
        arch = etree.fromstring(view_info["arch"].encode())
        field_names = [el.get("name") for el in arch.iter("field")]
        self.assertIn("last_quotation_date", field_names)
        self.assertIn("last_sale_date", field_names)
        self.assertIn("last_sale_delivery_date", field_names)

    def test_07_form_view_fields(self):
        """Check that date fields and stat button are in the combined form view arch."""
        view_info = self.env["res.partner"].get_view(view_type="form")
        arch = etree.fromstring(view_info["arch"].encode())
        field_names = [el.get("name") for el in arch.iter("field")]
        self.assertIn("last_quotation_date", field_names)
        self.assertIn("last_sale_date", field_names)
        self.assertIn("last_sale_delivery_date", field_names)
        self.assertIn("shipping_sale_order_count", field_names)
