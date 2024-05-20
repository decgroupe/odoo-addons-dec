# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, May 2024

import re

from odoo.tests.common import Form, TransactionCase
from odoo.tools import mute_logger
from odoo.exceptions import UserError, ValidationError


class TestSaleProductWarnings(TransactionCase):
    def setUp(self):
        super().setUp()
        self.so_2 = self.env.ref("sale.sale_order_2")
        self.product_9 = self.env.ref("product.product_product_9")

    def _create_so_line(self, order_id, product_id):
        res = self.env["sale.order.line"].create(
            {
                "order_id": order_id.id,
                "product_id": product_id.id,
            }
        )
        return res

    def _assert_activity_note(self, activity_id, note_parts):
        for note in note_parts:
            self.assertRegex(activity_id.note, note)

    def test_01_product_state_review(self):
        self.product_9.product_state_id = self.env.ref(
            "product_state_review.product_state_review"
        )
        self.assertEqual(len(self.so_2.activity_ids), 0)
        so_line = self._create_so_line(self.so_2, self.product_9)
        activity_id = self.so_2.activity_ids
        self.assertEqual(len(activity_id), 1)
        note_parts = [
            r"Please review the following product that was added to %s"
            % (self.so_2.name),
            r"\[E-COM10\] Pedal Bin",
        ]
        self._assert_activity_note(activity_id, note_parts)

    def test_02_product_state_quotation(self):
        self.product_9.product_state_id = self.env.ref(
            "product_state_review.product_state_quotation"
        )
        self.assertEqual(len(self.so_2.activity_ids), 0)
        so_line = self._create_so_line(self.so_2, self.product_9)
        activity_id = self.so_2.activity_ids
        self.assertEqual(len(activity_id), 0)

    def test_03_onchange_product_state_review(self):
        self.product_9.product_state_id = self.env.ref(
            "product_state_review.product_state_review"
        )
        with Form(self.so_2) as so_form:
            with so_form.order_line.new() as sol_form:
                with mute_logger("odoo.tests.common.onchange"):
                    sol_form.product_id = self.product_9
                    warning = sol_form._perform_onchange(["product_id"])["warning"]
                    self.assertEqual("Warning for Pedal Bin", warning["title"])
                    self.assertRegex(
                        warning["message"], r"This product needs to be reviewed"
                    )
                    self.assertRegex(warning["message"], r"No internal notes")
                    self.assertRegex(
                        warning["message"], r"No responsible for this product"
                    )

    def test_04_onchange_product_state_quotation(self):
        self.product_9.product_state_id = self.env.ref(
            "product_state_review.product_state_quotation"
        )
        with Form(self.so_2) as so_form:
            with so_form.order_line.new() as sol_form:
                with mute_logger("odoo.tests.common.onchange"):
                    sol_form.product_id = self.product_9
                    warning = sol_form._perform_onchange(["product_id"])["warning"]
                    self.assertEqual("Warning for Pedal Bin", warning["title"])
                    self.assertRegex(
                        warning["message"],
                        r"This product is currently in quotation, prices may not be correct",
                    )
                    self.assertRegex(warning["message"], r"No internal notes")
                    self.assertRegex(
                        warning["message"], r"No responsible for this product"
                    )

    def test_05_onchange_product_state_obsolete(self):
        self.product_9.product_state_id = self.env.ref(
            "product_state.product_state_obsolete"
        )
        with Form(self.so_2) as so_form:
            with so_form.order_line.new() as sol_form:
                with mute_logger("odoo.tests.common.onchange"):
                    sol_form.product_id = self.product_9
                    warning = sol_form._perform_onchange(["product_id"])["warning"]
                    self.assertEqual("Warning for Pedal Bin", warning["title"])
                    self.assertRegex(warning["message"], r"Obsolete product")
                    self.assertRegex(warning["message"], r"No internal notes")

    def test_06_onchange_product_state_normal(self):
        self.product_9.product_state_id = self.env.ref(
            "product_state.product_state_sellable"
        )
        with Form(self.so_2) as so_form:
            with so_form.order_line.new() as sol_form:
                with mute_logger("odoo.tests.common.onchange"):
                    sol_form.product_id = self.product_9
                    self.assertNotIn(
                        "warning", sol_form._perform_onchange(["product_id"])
                    )

    def test_07_blocking_message(self):
        self.env.user.groups_id = [(4, self.env.ref("sale.group_warning_sale").id)]
        self.product_9.sale_line_warn = "block_confirm"
        self.product_9.sale_line_warn_msg = "This is a test message"
        self.so_2.action_confirm()
        with self.assertRaisesRegex(
            ValidationError,
            re.compile(
                r"Following products are blocking.*This is a test message",
                re.MULTILINE | re.IGNORECASE | re.DOTALL,
            ),
        ):
            with Form(self.so_2) as so_form:
                with so_form.order_line.new() as sol_form:
                    sol_form.product_id = self.product_9
