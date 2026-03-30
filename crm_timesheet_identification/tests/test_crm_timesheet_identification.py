# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Mar 2026

from odoo.tests import new_test_user
from odoo.tests.common import TransactionCase


class TestCrmTimesheetIdentification(TransactionCase):
    """Tests for crm_timesheet_identification module."""

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
            login="crm_timesheet_identification-user",
            groups="sales_team.group_sale_salesman",
            context=ctx,
        )
        cls.crm_user.action_create_employee()
        cls.crm_employee = cls.crm_user.employee_id
        cls.model_analytic_line = cls.env["account.analytic.line"]
        cls.model_lead = cls.env["crm.lead"]
        cls.project = cls.env["project.project"].create({"name": "Test Project"})
        cls.lead = cls.model_lead.create(
            {"name": "Test Lead", "project_id": cls.project.id}
        )

    def _create_timesheet_line(self, lead=None):
        """Create a timesheet line optionally linked to a lead."""
        vals = {
            "name": "Test timesheet",
            "project_id": self.project.id,
            "employee_id": self.crm_employee.id,
            "unit_amount": 1,
        }
        if lead:
            vals["lead_id"] = lead.id
        return self.model_analytic_line.create(vals)

    def test_01_no_lead_gives_false(self):
        """A timesheet line without a lead has a False identification."""
        line = self._create_timesheet_line()
        self.assertFalse(line.lead_identification)

    def test_02_lead_gives_identification(self):
        """A timesheet line linked to a lead has a non-empty identification."""
        line = self._create_timesheet_line(lead=self.lead)
        self.assertTrue(line.lead_identification)
        expected = " / ".join(self.lead._get_name_identifications())
        self.assertEqual(line.lead_identification, expected)

    def test_03_lead_change_updates_identification(self):
        """Changing the lead on a timesheet line recomputes the identification."""
        line = self._create_timesheet_line()
        self.assertFalse(line.lead_identification)
        line.lead_id = self.lead
        expected = " / ".join(self.lead._get_name_identifications())
        self.assertEqual(line.lead_identification, expected)
        line.lead_id = False
        self.assertFalse(line.lead_identification)

    def test_04_identification_contains_lead_name(self):
        """The lead identification string contains the lead name."""
        line = self._create_timesheet_line(lead=self.lead)
        self.assertIn("Test Lead", line.lead_identification)
