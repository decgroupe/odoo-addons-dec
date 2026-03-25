# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Mar 2026

from odoo.tests import new_test_user
from odoo.tests.common import TransactionCase

from odoo.addons.project.models.project_task import CLOSED_STATES


class TestHrTimesheetTaskDomainOverride(TransactionCase):
    """Tests for hr_timesheet_task_domain_override module"""

    def setUp(self):
        super().setUp()
        ctx = {
            "mail_create_nolog": True,
            "mail_create_nosubscribe": True,
            "mail_notrack": True,
            "no_reset_password": True,
        }
        self.user = new_test_user(
            self.env,
            login="hr_timesheet_task_domain_override-user",
            groups="project.group_project_user",
            context=ctx,
        )
        self.user.action_create_employee()
        self.employee = self.user.employee_id
        self.project = self.env["project.project"].create(
            {"name": "Test Project", "allow_timesheets": True}
        )
        self.task = self.env["project.task"].create(
            {"name": "Test Task", "project_id": self.project.id}
        )

    def test_01_domain_without_project(self):
        """Without project_id, domain only filters by company and allow_timesheets."""
        al = self.env["account.analytic.line"].create(
            {
                "name": "Timesheet without project",
                "employee_id": self.employee.id,
                "unit_amount": 1,
            }
        )
        expected_domain = [
            ("company_id", "in", (al.company_id.id, False)),
            ("project_id.allow_timesheets", "=", True),
        ]
        self.assertEqual(
            al.task_id_domain,
            expected_domain,
            "Domain without project should only filter by company and allow_timesheets",
        )

    def test_02_domain_with_project(self):
        """With project_id (default context), domain includes project_id =? filter."""
        al = self.env["account.analytic.line"].create(
            {
                "name": "Timesheet with project",
                "project_id": self.project.id,
                "employee_id": self.employee.id,
                "unit_amount": 1,
            }
        )
        expected_domain = [
            ("company_id", "in", (al.company_id.id, False)),
            ("project_id.allow_timesheets", "=", True),
            ("project_id", "=?", self.project.id),
        ]
        self.assertEqual(
            al.task_id_domain,
            expected_domain,
            "Domain with project should include project_id =? filter",
        )

    def test_03_domain_with_project_keep_original(self):
        """With project_id and keep_hr_timesheet_task_domain context, closed tasks
        are excluded.
        """
        al = self.env["account.analytic.line"].create(
            {
                "name": "Timesheet with project and original domain",
                "project_id": self.project.id,
                "employee_id": self.employee.id,
                "unit_amount": 1,
            }
        )
        al_with_ctx = al.with_context(keep_hr_timesheet_task_domain=True)
        al_with_ctx._compute_task_id_domain()
        expected_domain = [
            ("company_id", "in", (al.company_id.id, False)),
            ("project_id.allow_timesheets", "=", True),
            ("state", "not in", list(CLOSED_STATES.keys())),
            ("project_id", "=", self.project.id),
        ]
        self.assertEqual(
            al.task_id_domain,
            expected_domain,
            "Domain with `keep_hr_timesheet_task_domain` context "
            "should exclude closed tasks",
        )

    def test_04_closed_task_visible_in_default_domain(self):
        """A closed task must match the default domain (no state filter)."""
        closed_state = list(CLOSED_STATES.keys())[0]
        closed_task = self.env["project.task"].create(
            {
                "name": "Closed Task",
                "project_id": self.project.id,
                "state": closed_state,
            }
        )
        al = self.env["account.analytic.line"].create(
            {
                "name": "Timesheet linked to closed task",
                "project_id": self.project.id,
                "task_id": closed_task.id,
                "employee_id": self.employee.id,
                "unit_amount": 1,
            }
        )
        domain = al.task_id_domain
        # closed task must be found using the computed domain
        matching_tasks = self.env["project.task"].search(domain)
        self.assertIn(
            closed_task,
            matching_tasks,
            "Closed task should be visible with the default domain (no state filter)",
        )

    def test_05_closed_task_hidden_with_keep_original_domain(self):
        """A closed task must NOT match the domain when keep_hr_timesheet_task_domain
        is set."""
        closed_state = list(CLOSED_STATES.keys())[0]
        closed_task = self.env["project.task"].create(
            {
                "name": "Closed Task",
                "project_id": self.project.id,
                "state": closed_state,
            }
        )
        al = self.env["account.analytic.line"].create(
            {
                "name": "Timesheet linked to closed task",
                "project_id": self.project.id,
                "task_id": closed_task.id,
                "employee_id": self.employee.id,
                "unit_amount": 1,
            }
        )
        al_with_ctx = al.with_context(keep_hr_timesheet_task_domain=True)
        al_with_ctx._compute_task_id_domain()
        domain = al.task_id_domain
        # closed task must NOT be found using the restricted domain
        matching_tasks = self.env["project.task"].search(domain)
        self.assertNotIn(
            closed_task,
            matching_tasks,
            "Closed task should NOT be visible when "
            "`keep_hr_timesheet_task_domain` is set",
        )
