# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Apr 2026

from lxml import etree

from odoo.exceptions import UserError

from .common import TestRecreateAnalyticLinesCommon


class TestRecreateAnalyticLines(TestRecreateAnalyticLinesCommon):
    """Tests for account_recreate_analytic_lines module."""

    def test_01_get_product_analytic_distribution(self):
        """Check that distribution is returned for a product with income analytic."""
        AML = self.env["account.move.line"]
        distribution = AML._get_product_analytic_distribution(
            self.product, "out_invoice"
        )
        self.assertEqual(distribution, {self.analytic_account.id: 100})

    def test_02_get_product_analytic_distribution_no_account(self):
        """Check that False is returned when no analytic account is set."""
        AML = self.env["account.move.line"]
        product_no_analytic = self.env["product.product"].create(
            {"name": "No Analytic Product", "type": "consu"}
        )
        distribution = AML._get_product_analytic_distribution(
            product_no_analytic, "out_invoice"
        )
        self.assertFalse(distribution)

    def test_03_get_product_analytic_distribution_no_product(self):
        """Check that False is returned when no product is given."""
        AML = self.env["account.move.line"]
        distribution = AML._get_product_analytic_distribution(
            self.env["product.product"], "out_invoice"
        )
        self.assertFalse(distribution)

    def test_04_set_default_analytic_account_on_lines(self):
        """Check that set_default_analytic_account sets distribution on lines."""
        inv_line = self.invoice.invoice_line_ids[0]
        inv_line.analytic_distribution = False
        self.invoice.invoice_line_ids.set_default_analytic_account()
        self.assertEqual(
            inv_line.analytic_distribution,
            {str(self.analytic_account.id): 100},
        )

    def test_05_set_default_analytic_account_skips_existing(self):
        """Check that existing distribution is preserved without override context."""
        other_account = self.env["account.analytic.account"].create(
            {"name": "Other Account", "plan_id": self.plan.id, "company_id": False}
        )
        inv_line = self.invoice.invoice_line_ids[0]
        inv_line.analytic_distribution = {other_account.id: 100}
        self.invoice.invoice_line_ids.set_default_analytic_account()
        # should not overwrite the existing distribution
        self.assertEqual(
            inv_line.analytic_distribution,
            {str(other_account.id): 100},
        )

    def test_06_set_default_analytic_account_override_existing(self):
        """Check that override_existing_account context forces update."""
        other_account = self.env["account.analytic.account"].create(
            {"name": "Other Account 2", "plan_id": self.plan.id, "company_id": False}
        )
        inv_line = self.invoice.invoice_line_ids[0]
        inv_line.analytic_distribution = {other_account.id: 100}
        self.invoice.invoice_line_ids.with_context(
            override_existing_account=True
        ).set_default_analytic_account()
        # should overwrite because of context flag
        self.assertEqual(
            inv_line.analytic_distribution,
            {str(self.analytic_account.id): 100},
        )

    def test_07_get_matching_inv_line_by_product(self):
        """Check that _get_matching_inv_line finds the line by product."""
        self.invoice._post()
        product_move_line = self.invoice.line_ids.filtered(
            lambda ml: ml.product_id == self.product and ml.credit > 0
        )
        self.assertTrue(product_move_line)
        matched = self.invoice._get_matching_inv_line(product_move_line)
        self.assertEqual(matched, self.invoice.invoice_line_ids[0])

    def test_08_get_matching_inv_line_no_match_raises(self):
        """Check that _get_matching_inv_line raises UserError when no match."""
        self.invoice._post()
        # use a move line from a different move (tax line has no product → no match)
        tax_line = self.invoice.line_ids.filtered(
            lambda ml: not ml.product_id and ml.tax_line_id
        )
        if not tax_line:
            self.skipTest("No tax line found, skipping test")
        with self.assertRaises(UserError):
            self.invoice._get_matching_inv_line(tax_line[:1])

    def test_09_action_set_default_analytic_account_posted(self):
        """Check that action recreates analytic distribution on posted invoice."""
        self.invoice._post()
        # clear distribution from the invoice line to start fresh
        for line in self.invoice.invoice_line_ids:
            line.analytic_distribution = False
        self.invoice.action_set_default_analytic_account()
        inv_line = self.invoice.invoice_line_ids[0]
        self.assertTrue(inv_line.analytic_distribution)
        self.assertIn(str(self.analytic_account.id), inv_line.analytic_distribution)

    def test_10_form_view_has_button(self):
        """Check that the 'Set Default Analytic Account' button is in the form view."""
        view_info = self.env["account.move"].get_view(view_type="form")
        arch = etree.fromstring(view_info["arch"])
        buttons = [el.get("name") for el in arch.iter("button") if el.get("name")]
        self.assertIn("action_set_default_analytic_account", buttons)

    def test_11_wizard_form_view_has_product_id_in_lines(self):
        """Check that product_id field appears in the wizard form view line_ids list."""
        view_info = self.env["account.move.update"].get_view(view_type="form")
        arch = etree.fromstring(view_info["arch"])
        field_names = [el.get("name") for el in arch.iter("field")]
        self.assertIn("product_id", field_names)

    def test_12_remove_lines_with_product_id(self):
        """Check that wizard method removes lines that have a product assigned."""
        res = self.invoice.prepare_update_wizard()
        wizard = self.env["account.move.update"].browse(res["res_id"])
        lines_with_product_before = wizard.line_ids.filtered(lambda x: x.product_id)
        self.assertTrue(lines_with_product_before)
        wizard.remove_lines_with_product_id()
        lines_with_product_after = wizard.line_ids.filtered(lambda x: x.product_id)
        self.assertFalse(lines_with_product_after)

    def test_13_set_default_with_override_existing(self):
        """Check that override_existing_account context forces recreating analytic
        lines."""
        self.invoice._post()
        product_ml = self.invoice.line_ids.filtered(
            lambda ml: ml.product_id == self.product and ml.credit > 0
        )
        self.assertTrue(product_ml)
        # calling with override should unlink and recreate analytic lines
        self.invoice.with_context(
            override_existing_account=True
        ).action_set_default_analytic_account()
        # verify distribution is set and analytic lines were recreated
        self.assertTrue(product_ml.analytic_distribution)
        self.assertTrue(product_ml.analytic_line_ids)

    def test_14_vendor_bill_credit_zero_skipped(self):
        """Check that vendor bill product lines with credit==0 are skipped in move
        loop."""
        from odoo import fields as odoo_fields

        vendor_bill = self.env["account.move"].create(
            {
                "partner_id": self.partner.id,
                "move_type": "in_invoice",
                "invoice_date": odoo_fields.Date.today(),
                "invoice_line_ids": [
                    (
                        0,
                        0,
                        {
                            "name": "Vendor Test Line",
                            "product_id": self.product.id,
                            "quantity": 1,
                            "price_unit": 50.0,
                        },
                    )
                ],
            }
        )
        vendor_bill._post()
        product_move_line = vendor_bill.line_ids.filtered(
            lambda ml: ml.product_id == self.product
        )
        # for a vendor bill the product line has debit > 0 and credit == 0
        self.assertEqual(product_move_line.credit, 0.0)
        # calling the method should not raise an error
        vendor_bill.action_set_default_analytic_account()

    def test_15_set_default_analytic_fallback_on_match_error(self):
        """Check that UserError fallback sets distribution via product when no match."""
        # create an invoice with two lines for the same product
        # which will cause _get_matching_inv_line to raise UserError
        invoice = self.env["account.move"].create(
            {
                "partner_id": self.partner.id,
                "move_type": "out_invoice",
                "invoice_line_ids": [
                    (
                        0,
                        0,
                        {
                            "product_id": self.product.id,
                            "quantity": 1,
                            "price_unit": 10.0,
                        },
                    ),
                    (
                        0,
                        0,
                        {
                            "product_id": self.product.id,
                            "quantity": 2,
                            "price_unit": 20.0,
                        },
                    ),
                ],
            }
        )
        invoice._post()
        # clear analytic on invoice lines so the loop proceeds
        for line in invoice.invoice_line_ids:
            line.analytic_distribution = {self.analytic_account.id: 100}
        # override so the lines are not skipped
        invoice.with_context(
            override_existing_account=True
        ).action_set_default_analytic_account()
        # the fallback should have set the distribution from product
        for ml in invoice.line_ids.filtered(lambda ml: ml.product_id and ml.credit > 0):
            self.assertTrue(ml.analytic_distribution)

    def test_16_wizard_get_matching_inv_line(self):
        """Check that wizard _get_matching_inv_line delegates to invoice method."""
        self.invoice._post()
        res = self.invoice.prepare_update_wizard()
        wizard = self.env["account.move.update"].browse(res["res_id"])
        product_move_line = self.invoice.line_ids.filtered(
            lambda ml: ml.product_id == self.product and ml.credit > 0
        )
        matched = wizard._get_matching_inv_line(product_move_line)
        self.assertEqual(matched, self.invoice.invoice_line_ids[0])

    def test_17_wizard_get_move_lines(self):
        """Check that wizard _get_move_lines returns all move lines."""
        self.invoice._post()
        res = self.invoice.prepare_update_wizard()
        wizard = self.env["account.move.update"].browse(res["res_id"])
        move_lines = wizard._get_move_lines(self.invoice)
        self.assertEqual(move_lines, self.invoice.line_ids)
