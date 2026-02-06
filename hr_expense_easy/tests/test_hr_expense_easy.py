# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, May 2026

from freezegun import freeze_time

from odoo import Command
from odoo.exceptions import UserError

from .common import TestHrExpenseEasyCommon


class TestHrExpenseEasy(TestHrExpenseEasyCommon):
    """Tests for hr_expense_easy module."""

    def test_01_default_sheet_name_format(self):
        """Check the default sheet name format is YYYY/MM-MonthName."""
        # freeze to Jan 15, 2026 -> date - 10 days = Jan 5, 2026 -> "2026/01-January"
        with freeze_time("2026-01-15"):
            sheet = self.env["hr.expense.sheet"].new({"employee_id": self.employee.id})
            self.assertEqual(sheet.name, "2026/01-January")

    def test_02_default_sheet_name_boundary(self):
        """Check the sheet name boundary: Dec 11 uses December, Dec 10 uses November."""
        # dec 20 -> date - 10 days = dec 10 -> month 12 -> "2025/12-December"
        with freeze_time("2025-12-20"):
            sheet_dec = self.env["hr.expense.sheet"].new(
                {"employee_id": self.employee.id}
            )
            self.assertEqual(sheet_dec.name, "2025/12-December")
        # dec 10 -> date - 10 days = nov 30 -> month 11 -> "2025/11-November"
        with freeze_time("2025-12-10"):
            sheet_nov = self.env["hr.expense.sheet"].new(
                {"employee_id": self.employee.id}
            )
            self.assertEqual(sheet_nov.name, "2025/11-November")

    def test_03_product_has_cost_always_true(self):
        """Check that product_has_cost is always True regardless of standard_price."""
        # product with standard_price=0 should still have product_has_cost=True
        expense_no_cost = self._make_expense(
            total_amount=100.0, tax_ids=[self.tax_incl.id]
        )
        self.assertTrue(expense_no_cost.product_has_cost)
        # product with standard_price>0 should also have product_has_cost=True
        expense_with_cost = self.env["hr.expense"].create(
            {
                "name": "Expense with cost product",
                "employee_id": self.employee.id,
                "product_id": self.product_with_cost.id,
                "total_amount_currency": 100.0,
            }
        )
        self.assertTrue(expense_with_cost.product_has_cost)

    def test_04_price_unit_not_computed_from_product(self):
        """Check that price_unit is computed from total_amount, not product cost."""
        # product_with_cost has standard_price=50, but module disables cost-based
        # computation
        expense = self.env["hr.expense"].create(
            {
                "name": "Expense with cost product",
                "employee_id": self.employee.id,
                "product_id": self.product_with_cost.id,
                "total_amount_currency": 120.0,
            }
        )
        # price_unit must reflect total_amount, not the product standard_price
        self.assertAlmostEqual(expense.price_unit, 120.0, places=2)
        self.assertFalse(expense._needs_product_price_computation())

    def test_05_automatic_tax_amount_true(self):
        """Check that automatic_tax_amount is True when tax is not manually
        overridden."""
        expense = self._make_expense(total_amount=100.0, tax_ids=[self.tax_incl.id])
        # manual_tax_amount should be equal to the computed tax_amount
        self.assertTrue(expense.automatic_tax_amount)
        self.assertAlmostEqual(expense.manual_tax_amount, expense.tax_amount, places=2)

    def test_06_manual_tax_override(self):
        """Check that manually overriding manual_tax_amount affects
        tax_amount_currency."""
        expense = self._make_expense(total_amount=100.0, tax_ids=[self.tax_incl.id])
        self.assertTrue(expense.automatic_tax_amount)
        # manually set a different tax amount
        expense.write({"manual_tax_amount": 5.0})
        # automatic_tax_amount must now be False
        self.assertFalse(expense.automatic_tax_amount)
        # tax_amount_currency must use the manual override
        self.assertAlmostEqual(expense.tax_amount_currency, 5.0, places=2)
        # untaxed_amount_currency must be total - manual_tax
        self.assertAlmostEqual(expense.untaxed_amount_currency, 95.0, places=2)

    def test_07_tax_price_include_validation(self):
        """Check that UserError is raised when a non-price-include tax is used."""
        # in Odoo 18, price_include is computed - use price_include_override
        tax_excl = self.env["account.tax"].create(
            {
                "name": "Test VAT 20% excl",
                "amount": 20.0,
                "type_tax_use": "purchase",
                "price_include_override": "tax_excluded",
                "amount_type": "percent",
            }
        )
        expense = self._make_expense(total_amount=100.0, tax_ids=[])
        # the UserError may be raised during write() (immediate flush) or
        # during flush_recordset() (deferred recomputation) - both are valid
        with self.assertRaises(UserError):
            expense.write({"tax_ids": [Command.set([tax_excl.id])]})
            expense.flush_recordset(["tax_amount_currency"])

    def test_08_expense_duplicate(self):
        """Check that action_duplicate creates a copy of the expense."""
        sheet = self._make_sheet()
        expense = self._make_expense(
            total_amount=100.0,
            tax_ids=[self.tax_incl.id],
            sheet=sheet,
        )
        expense_count_before = self.env["hr.expense"].search_count(
            [("sheet_id", "=", sheet.id)]
        )
        expense.action_duplicate()
        expense_count_after = self.env["hr.expense"].search_count(
            [("sheet_id", "=", sheet.id)]
        )
        self.assertEqual(expense_count_after, expense_count_before + 1)

    def test_09_expense_duplicate_blocked_when_approved(self):
        """Check that action_duplicate raises UserError for approved expenses."""
        sheet = self._make_sheet()
        expense = self._make_expense(
            total_amount=100.0,
            tax_ids=[self.tax_incl.id],
            sheet=sheet,
        )
        # set the sheet to approved state using sudo to bypass access checks
        sheet.sudo().write({"approval_state": "approve"})
        # expense state should now be 'approved' (from sheet.state = 'approve')
        self.assertEqual(expense.state, "approved")
        with self.assertRaises(UserError):
            expense.action_duplicate()

    def test_10_sheet_amount_with_mixed_taxes(self):
        """Check sheet total_tax_amount uses manual_tax_amount for manual expenses."""
        sheet = self._make_sheet()
        # expense 1: automatic tax
        expense_auto = self._make_expense(
            total_amount=100.0,
            tax_ids=[self.tax_incl.id],
            sheet=sheet,
        )
        # expense 2: manual tax override
        expense_manual = self._make_expense(
            total_amount=100.0,
            tax_ids=[self.tax_incl.id],
            sheet=sheet,
        )
        expense_manual.write({"manual_tax_amount": 5.0})
        self.assertFalse(expense_manual.automatic_tax_amount)
        # sheet total_tax_amount must sum auto tax_amount + manual override
        expected_tax = expense_auto.tax_amount + 5.0
        self.assertAlmostEqual(sheet.total_tax_amount, expected_tax, places=2)
        # untaxed_amount must be total_amount - total_tax_amount
        self.assertAlmostEqual(
            sheet.untaxed_amount, sheet.total_amount - expected_tax, places=2
        )

    def test_11_expense_sheet_view_fields(self):
        """Check that expected fields are present in the expense sheet form view."""
        from lxml import etree

        view_info = self.env["hr.expense.sheet"].get_view(view_type="form")
        arch = etree.fromstring(view_info["arch"].encode())
        field_names = [el.get("name") for el in arch.iter("field")]
        self.assertIn("manual_tax_amount", field_names)
        self.assertIn("automatic_tax_amount", field_names)
        self.assertIn("untaxed_amount_currency", field_names)

    def test_12_default_sheet_name_remaining_months(self):
        """Check default sheet name for all months not covered in other tests."""
        months = [
            ("2025-02-15", "2025/02-February"),
            ("2025-03-15", "2025/03-March"),
            ("2025-04-15", "2025/04-April"),
            ("2025-05-15", "2025/05-May"),
            ("2025-06-15", "2025/06-June"),
            ("2025-07-15", "2025/07-July"),
            ("2025-08-15", "2025/08-August"),
            ("2025-09-15", "2025/09-September"),
            ("2025-10-15", "2025/10-October"),
        ]
        for frozen_date, expected_name in months:
            with freeze_time(frozen_date):
                sheet = self.env["hr.expense.sheet"].new(
                    {"employee_id": self.employee.id}
                )
                self.assertEqual(
                    sheet.name,
                    expected_name,
                    msg=f"expected {expected_name} for frozen date {frozen_date}",
                )

    def test_13_get_attachment_view_no_attachment(self):
        """Check action_get_attachment_view returns create form when no attachment."""
        expense = self._make_expense(total_amount=50.0, tax_ids=[])
        self.assertEqual(expense.nb_attachment, 0)
        action = expense.action_get_attachment_view()
        self.assertEqual(action["res_model"], "ir.attachment")
        self.assertEqual(action["view_mode"], "form")
        self.assertEqual(action["target"], "new")
        self.assertIn("default_res_id", action["context"])

    def test_14_get_attachment_view_with_attachment(self):
        """Check action_get_attachment_view calls super when attachment exists."""
        expense = self._make_expense(total_amount=50.0, tax_ids=[])
        # create an attachment linked to the expense
        self.env["ir.attachment"].create(
            {
                "name": "test.pdf",
                "res_model": expense._name,
                "res_id": expense.id,
                "type": "binary",
                "datas": b"test",
            }
        )
        self.assertEqual(expense.nb_attachment, 1)
        action = expense.action_get_attachment_view()
        # super() returns the standard attachment list view (not the create form)
        self.assertIsNotNone(action)
