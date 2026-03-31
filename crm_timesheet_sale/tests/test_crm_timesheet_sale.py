# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Sep 2023

from odoo.tests import Form, new_test_user
from odoo.tests.common import TransactionCase


class TestCrmTimesheetSale(TransactionCase):
    """Tests for crm_timesheet_sale module."""

    @classmethod
    def setUpClass(cls):
        """Set up shared test data."""
        super().setUpClass()
        ctx = {
            "mail_create_nolog": True,
            "mail_create_nosubscribe": True,
            "mail_notrack": True,
            "no_reset_password": True,
        }
        cls.crm_user = new_test_user(
            cls.env,
            login="crm_timesheet_sale-user",
            groups="sales_team.group_sale_salesman",
            context=ctx,
        )
        cls.crm_user.action_create_employee()
        cls.crm_employee = cls.crm_user.employee_id
        cls.project = cls.env["project.project"].create({"name": "Test Project"})
        cls.lead = cls.env["crm.lead"].create(
            {
                "name": "Test Opportunity",
                "type": "opportunity",
                "project_id": cls.project.id,
            }
        )
        cls.partner = cls.env["res.partner"].create({"name": "Test Partner"})
        cls.sale_order = cls.env["sale.order"].create(
            {
                "partner_id": cls.partner.id,
                "opportunity_id": cls.lead.id,
            }
        )

    def test_01_sale_id_default_false(self):
        """Verify sale_id defaults to False on a new timesheet line."""
        line = self.env["account.analytic.line"].create(
            {
                "name": "Test Timesheet",
                "project_id": self.project.id,
                "employee_id": self.crm_employee.id,
                "unit_amount": 1,
            }
        )
        self.assertFalse(line.sale_id)

    def test_02_sale_id_set_on_line(self):
        """Verify sale_id can be set to a sale order on a timesheet line."""
        line = self.env["account.analytic.line"].create(
            {
                "name": "Test Timesheet",
                "project_id": self.project.id,
                "lead_id": self.lead.id,
                "employee_id": self.crm_employee.id,
                "unit_amount": 1,
                "sale_id": self.sale_order.id,
            }
        )
        self.assertEqual(line.sale_id, self.sale_order)
        self.assertEqual(line.sale_id.opportunity_id, self.lead)

    def test_03_sale_id_invisible_without_lead(self):
        """Verify sale_id is invisible in the form when lead_id is not set."""
        line = self.env["account.analytic.line"].create(
            {
                "name": "Test Timesheet",
                "project_id": self.project.id,
                "employee_id": self.crm_employee.id,
                "unit_amount": 1,
            }
        )
        view = "crm_timesheet_sale.hr_timesheet_line_form_view"
        with Form(line, view=view) as form:
            self.assertTrue(form._get_modifier("sale_id", "invisible"))

    def test_04_sale_id_visible_with_lead(self):
        """Verify sale_id is visible in the form when lead_id is set."""
        line = self.env["account.analytic.line"].create(
            {
                "name": "Test Timesheet",
                "project_id": self.project.id,
                "lead_id": self.lead.id,
                "employee_id": self.crm_employee.id,
                "unit_amount": 1,
            }
        )
        view = "crm_timesheet_sale.hr_timesheet_line_form_view"
        with Form(line, view=view) as form:
            self.assertFalse(form._get_modifier("sale_id", "invisible"))
