# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, May 2026


from odoo import Command
from odoo.tests.common import TransactionCase


class TestHrExpenseEasyCommon(TransactionCase):
    """Base class with shared fixtures for hr_expense_easy tests."""

    @classmethod
    def setUpClass(cls):
        """Set up shared test data."""
        super().setUpClass()
        # create a tax with price_include=True (required by the module);
        # in Odoo 18, price_include is computed - use price_include_override
        cls.tax_incl = cls.env["account.tax"].create(
            {
                "name": "Test VAT 20% incl",
                "amount": 20.0,
                "type_tax_use": "purchase",
                "price_include_override": "tax_included",
                "amount_type": "percent",
            }
        )
        # create a product that can be expensed
        cls.product = cls.env["product.product"].create(
            {
                "name": "Test Expense Product",
                "type": "service",
                "can_be_expensed": True,
                "standard_price": 0.0,
                "supplier_taxes_id": [Command.set([cls.tax_incl.id])],
            }
        )
        # create a product with a non-zero cost to test product_has_cost override
        cls.product_with_cost = cls.env["product.product"].create(
            {
                "name": "Test Expense Product with Cost",
                "type": "service",
                "can_be_expensed": True,
                "standard_price": 50.0,
            }
        )
        # create an employee
        cls.employee = cls.env["hr.employee"].create({"name": "Test Employee"})

    def _make_expense(self, total_amount=100.0, tax_ids=None, sheet=None):
        """Create a simple expense record for testing."""
        vals = {
            "name": "Test Expense",
            "employee_id": self.employee.id,
            "product_id": self.product.id,
            "total_amount_currency": total_amount,
        }
        if tax_ids is not None:
            vals["tax_ids"] = [Command.set(tax_ids)]
        if sheet is not None:
            vals["sheet_id"] = sheet.id
        return self.env["hr.expense"].create(vals)

    def _make_sheet(self):
        """Create a simple expense sheet for testing."""
        return self.env["hr.expense.sheet"].create(
            {
                "name": "Test Sheet",
                "employee_id": self.employee.id,
            }
        )
