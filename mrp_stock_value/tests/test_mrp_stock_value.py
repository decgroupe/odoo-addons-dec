# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Apr 2026

from lxml import etree

from odoo.addons.website.tools import MockRequest

from .common import TestMrpStockValueCommon


class TestMrpStockValue(TestMrpStockValueCommon):
    """Tests for mrp_stock_value module."""

    def test_01_consumed_value_with_history(self):
        """Consumed value reflects component purchase price from history."""
        # complete the MO so move dates are set, then create history at that date
        mo = self._create_and_complete_mo()
        move_date = mo.move_raw_ids[0].date
        self.env["product.prices.history"].create(
            {
                "product_id": self.product_component.id,
                "type": "purchase",
                "purchase_price": 10.0,
                "datetime": move_date,
            }
        )
        # invalidate to re-trigger the compute
        mo.invalidate_recordset()
        self.assertAlmostEqual(mo.consumed_value, 10.0)

    def test_02_consumed_value_no_history(self):
        """Consumed value is 0 when no price history exists."""
        mo = self._create_and_complete_mo()
        self.assertAlmostEqual(mo.consumed_value, 0.0)

    def test_03_message_posted_after_mark_done(self):
        """A chatter message with consumed value is posted after button_mark_done."""
        mo = self.env["mrp.production"].create(
            {
                "product_id": self.product_finished.id,
                "bom_id": self.bom.id,
                "product_qty": 1.0,
            }
        )
        mo.action_confirm()
        mo.qty_producing = mo.product_qty
        mo.move_raw_ids.picked = True
        mo.button_mark_done()
        messages = mo.message_ids.filtered(lambda m: "Consumed value" in m.body)
        self.assertTrue(messages, "No consumed value message found in chatter")

    def test_04_form_view_fields(self):
        """Consumed value and currency fields appear in the combined form view arch."""
        with MockRequest(self.env) as mock:
            # simulate a debug HTTP request so base.group_no_one is active
            mock.session.debug = True
            self.assertTrue(self.env.user.has_group("base.group_no_one"))
            view_info = self.env["mrp.production"].get_view(view_type="form")
        arch = etree.fromstring(view_info["arch"].encode())
        field_names = [el.get("name") for el in arch.iter("field")]
        self.assertIn("consumed_value", field_names)
        self.assertIn("company_currency_id", field_names)
