# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Mar 2026

from datetime import datetime, timedelta

# from dateutil.relativedelta import relativedelta
from odoo.tests import Form, new_test_user
from odoo.tests.common import TransactionCase


class TestHelpdeskTimesheetTicketContext(TransactionCase):
    """Tests for helpdesk_timesheet_ticket_context module"""

    def setUp(self):
        super().setUp()
        ctx = {
            "mail_create_nolog": True,
            "mail_create_nosubscribe": True,
            "mail_notrack": True,
            "no_reset_password": True,
        }
        self.helpdesk_user = new_test_user(
            self.env,
            login="helpdesk_timesheet_ticket_context-user",
            groups="helpdesk_mgmt.group_helpdesk_user",
            context=ctx,
        )
        self.helpdesk_user.action_create_employee()
        self.helpdesk_employee = self.helpdesk_user.employee_id

    def test_01_timesheet_entry(self):
        today = datetime.today()
        project_id = self.env["project.project"].create({"name": "Project"})
        ticket1_id = self.env["helpdesk.ticket"].create(
            {
                "name": "Ticket 1",
                "project_id": project_id.id,
                "description": "This is a test ticket",
            }
        )
        # create a first timesheet entry for this ticket
        _al1 = self.env["account.analytic.line"].create(
            {
                "name": "Picking products from stock",
                "project_id": project_id.id,
                "ticket_id": ticket1_id.id,
                "employee_id": self.helpdesk_employee.id,
                "unit_amount": 1,  # one hour
                "date": ticket1_id.create_date,
            }
        )
        another_project_id = self.env["project.project"].create(
            {"name": "Another project"}
        )
        # create unrelated timesheet entries
        al2 = self.env["account.analytic.line"].create(
            {
                "name": "Contact our customer",
                "project_id": another_project_id.id,
                "employee_id": self.helpdesk_employee.id,
                "unit_amount": 1,  # one hour
                "date": today + timedelta(hours=1),
            }
        )
        al3 = self.env["account.analytic.line"].create(
            {
                "name": "Preparing demonstration",
                "project_id": another_project_id.id,
                "employee_id": self.helpdesk_employee.id,
                "unit_amount": 1,  # one hour
                "date": today + timedelta(hours=2),
            }
        )
        # assign ticket to the unrelated timesheet entry (using UI)
        al2_form = Form(
            al2, view="helpdesk_timesheet_ticket_context.hr_timesheet_line_form_view"
        )
        al2_form.project_id = self.env["project.project"]  # mandatory unset
        al2_form.ticket_id = ticket1_id
        al2_form.save()
        self.assertEqual(
            al2.project_id,
            ticket1_id.project_id,
            "Timesheet entry should now have the same project as the ticket",
        )
        # unassigning the ticket should not change the project
        al2_form = Form(
            al2, view="helpdesk_timesheet_ticket_context.hr_timesheet_line_form_view"
        )
        al2_form.ticket_id = self.env["helpdesk.ticket"]  # unassign ticket
        al2_form.save()
        self.assertEqual(
            al2.project_id,
            ticket1_id.project_id,
            "Timesheet entry should have kept its project",
        )
        # assign ticket to the second unrelated timesheet entry (using UI)
        # without clearing the project_id
        # note: contrary to `mrp_timesheet`, the project is replaced in this case
        al3_form = Form(
            al3, view="helpdesk_timesheet_ticket_context.hr_timesheet_line_form_view"
        )
        al3_form.ticket_id = ticket1_id
        al3_form.save()
        self.assertEqual(
            al3.project_id,
            ticket1_id.project_id,
            "Timesheet entry should have its project replaced by the one of the ticket",
        )
