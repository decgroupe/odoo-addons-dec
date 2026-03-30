# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Mar 2026

from odoo.tests import Form, new_test_user
from odoo.tests.common import TransactionCase


class TestHrTimesheetHelpdeskIdentification(TransactionCase):
    """Tests for hr_timesheet_helpdesk_identification module."""

    def setUp(self):
        """Set up shared test data."""
        super().setUp()
        ctx = {
            "mail_create_nolog": True,
            "mail_create_nosubscribe": True,
            "mail_notrack": True,
            "no_reset_password": True,
        }
        self.helpdesk_user = new_test_user(
            self.env,
            login="hr_timesheet_helpdesk_identification-user",
            groups="helpdesk_mgmt.group_helpdesk_user",
            context=ctx,
        )
        self.helpdesk_user.action_create_employee()
        self.helpdesk_employee = self.helpdesk_user.employee_id
        self.project = self.env["project.project"].create({"name": "Test Project"})
        self.ticket = self.env["helpdesk.ticket"].create(
            {
                "name": "Test Ticket",
                "description": "This is a test ticket",
                "project_id": self.project.id,
            }
        )

    def test_01_ticket_identification_computed(self):
        """ticket_identification is computed when a ticket is linked to a timesheet."""
        al = self.env["account.analytic.line"].create(
            {
                "name": "Work on ticket",
                "project_id": self.project.id,
                "ticket_id": self.ticket.id,
                "employee_id": self.helpdesk_employee.id,
                "unit_amount": 1,
                "date": self.ticket.create_date,
            }
        )
        self.assertTrue(al.ticket_identification)
        identifications = self.ticket._get_name_identifications()
        expected = " / ".join(identifications)
        self.assertEqual(al.ticket_identification, expected)

    def test_02_ticket_identification_empty_without_ticket(self):
        """ticket_identification is False when no ticket is linked to the timesheet."""
        al = self.env["account.analytic.line"].create(
            {
                "name": "Work without ticket",
                "project_id": self.project.id,
                "employee_id": self.helpdesk_employee.id,
                "unit_amount": 1,
            }
        )
        self.assertFalse(al.ticket_identification)

    def test_03_view_field_invisible_without_ticket(self):
        """ticket_identification is invisible in form view when no ticket is linked."""
        al = self.env["account.analytic.line"].create(
            {
                "name": "Work without ticket",
                "project_id": self.project.id,
                "employee_id": self.helpdesk_employee.id,
                "unit_amount": 1,
            }
        )
        view = "helpdesk_timesheet_ticket_context.hr_timesheet_line_form_view"
        with Form(al, view=view) as form:
            self.assertTrue(form._get_modifier("ticket_identification", "invisible"))

    def test_04_view_field_visible_with_ticket(self):
        """ticket_identification is visible in form view when a ticket is linked."""
        al = self.env["account.analytic.line"].create(
            {
                "name": "Work on ticket",
                "project_id": self.project.id,
                "ticket_id": self.ticket.id,
                "employee_id": self.helpdesk_employee.id,
                "unit_amount": 1,
                "date": self.ticket.create_date,
            }
        )
        view = "helpdesk_timesheet_ticket_context.hr_timesheet_line_form_view"
        with Form(al, view=view) as form:
            self.assertFalse(form._get_modifier("ticket_identification", "invisible"))
