# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Feb 2026

from datetime import datetime, timedelta

# from dateutil.relativedelta import relativedelta
from odoo.tests import Form, new_test_user
from odoo.tests.common import TransactionCase


class TestCrmTimesheetLeadContext(TransactionCase):
    def setUp(self):
        super().setUp()
        ctx = {
            "mail_create_nolog": True,
            "mail_create_nosubscribe": True,
            "mail_notrack": True,
            "no_reset_password": True,
        }
        self.crm_user = new_test_user(
            self.env,
            login="crm_timesheet_lead_context-user",
            groups="sales_team.group_sale_salesman",
            context=ctx,
        )
        self.crm_user.action_create_employee()
        self.crm_employee = self.crm_user.employee_id

    def test_01_timesheet_entry_production_data(self):
        today = datetime.today()
        project_id = self.env["project.project"].create({"name": "Project"})
        lead1_id = self.env["crm.lead"].create(
            {"name": "Lead 1", "project_id": project_id.id}
        )
        # create a first timesheet entry for this lead
        _al1 = self.env["account.analytic.line"].create(
            {
                "name": "Picking products from stock",
                "project_id": project_id.id,
                "lead_id": lead1_id.id,
                "employee_id": self.crm_employee.id,
                "unit_amount": 1,  # one hour
                "date": lead1_id.create_date,
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
                "employee_id": self.crm_employee.id,
                "unit_amount": 1,  # one hour
                "date": today + timedelta(hours=1),
            }
        )
        al3 = self.env["account.analytic.line"].create(
            {
                "name": "Preparing demonstration",
                "project_id": another_project_id.id,
                "employee_id": self.crm_employee.id,
                "unit_amount": 1,  # one hour
                "date": today + timedelta(hours=2),
            }
        )
        # assign lead to the unrelated timesheet entry (using UI)
        al2_form = Form(
            al2, view="crm_timesheet_lead_context.hr_timesheet_line_form_view"
        )
        al2_form.project_id = self.env["project.project"]  # mandatory unset
        al2_form.lead_id = lead1_id
        al2_form.save()
        self.assertEqual(
            al2.project_id,
            lead1_id.project_id,
            "Timesheet entry should now have the same project as the lead",
        )
        # unassigning the lead should not change the project
        al2_form = Form(
            al2, view="crm_timesheet_lead_context.hr_timesheet_line_form_view"
        )
        al2_form.lead_id = self.env["crm.lead"]  # unassign lead
        al2_form.save()
        self.assertEqual(
            al2.project_id,
            lead1_id.project_id,
            "Timesheet entry should have kept its project",
        )
        # assign lead to the second unrelated timesheet entry (using UI)
        # without clearing the project_id
        # note: contrary to `mrp_timesheet`, the project is replaced in this case
        al3_form = Form(
            al3, view="crm_timesheet_lead_context.hr_timesheet_line_form_view"
        )
        al3_form.lead_id = lead1_id
        al3_form.save()
        self.assertEqual(
            al3.project_id,
            lead1_id.project_id,
            "Timesheet entry should have its project replaced by the one of the lead",
        )
