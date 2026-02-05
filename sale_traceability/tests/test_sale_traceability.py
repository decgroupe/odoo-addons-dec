# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Feb 2026

import logging

from odoo import Command
from odoo.tests.common import TransactionCase, new_test_user

from ..models.sale_order import SALE_STATE_SYMBOLS

_logger = logging.getLogger(__name__)


class TestSaleTraceability(TransactionCase):
    """Tests for Sale Traceability module."""

    def _check_states(self, state_symbol_dict, model_name, field_name="state"):
        model = self.env[model_name]
        state_field = model._fields[field_name]
        states = [s[0] for s in state_field.selection]
        # ensure that all hard-coded states have a symbol match
        for state in states:
            self.assertIn(state, state_symbol_dict)
        # just check that no extra symbol is defined in the other way
        unknown_states = [s for s in state_symbol_dict.keys() if s not in states]
        if unknown_states:
            msg = f"`{model_name}` state symbol dict defined for unknown states:"
            for s in unknown_states:
                msg += f"\n\t- {s}"
            _logger.warning(msg)

    @classmethod
    def setUpClass(cls):
        super().setUpClass()

    def setUp(self):
        super().setUp()

    def test_01_sale_order_states(self):
        """Tests that all hard-coded sale order states have a symbol match"""
        self._check_states(SALE_STATE_SYMBOLS, "sale.order")

    def test_02_sale_head_description(self):
        ctx = {
            "mail_create_nolog": True,
            "mail_create_nosubscribe": True,
            "mail_notrack": True,
            "no_reset_password": True,
        }
        sale_user = new_test_user(
            self.env,
            login="action_view-user",
            groups="sales_team.group_sale_salesman",
            context=ctx,
        )
        sale_order = (
            self.env["sale.order"]
            .with_user(sale_user)
            .create(
                {
                    "partner_id": self.env.ref("base.res_partner_12").id,
                    "order_line": [
                        Command.create(
                            {
                                "product_id": self.env.ref(
                                    "product.product_product_5"
                                ).id,
                            },
                        )
                    ],
                }
            )
        )
        so_name = f"📈{sale_order.name}"
        head, desc = sale_order.order_line[0].get_head_desc()
        self.assertEqual(head, so_name)
        self.assertEqual(desc, "🏳️Quotation")
        # quotation sent
        sale_order.action_quotation_sent()
        head, desc = sale_order.order_line[0].get_head_desc()
        self.assertEqual(head, so_name)
        self.assertEqual(desc, "📩Quotation Sent")
        # confirm order
        sale_order.action_confirm()
        head, desc = sale_order.order_line[0].get_head_desc()
        self.assertEqual(head, so_name)
        self.assertEqual(desc, "💲Sales Order")
        # cancel order
        sale_order._action_cancel()
        head, desc = sale_order.order_line[0].get_head_desc()
        self.assertEqual(head, so_name)
        self.assertEqual(desc, "❌Cancelled")
