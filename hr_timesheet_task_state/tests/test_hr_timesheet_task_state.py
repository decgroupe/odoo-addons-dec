# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Mar 2026

from odoo.tests import Form
from odoo.tests.common import TransactionCase


class TestHrTimesheetTaskState(TransactionCase):
    """Tests for hr_timesheet_task_state module."""

    @classmethod
    def setUpClass(cls):
        """Set up shared test data."""
        super().setUpClass()
        cls.project = cls.env["project.project"].create({"name": "Test Project"})
        cls.stage = cls.env["project.task.type"].create(
            {"name": "In Progress", "project_ids": [cls.project.id]}
        )
        cls.task = cls.env["project.task"].create(
            {
                "name": "Test Task",
                "project_id": cls.project.id,
                "stage_id": cls.stage.id,
            }
        )
        cls.employee = cls.env["hr.employee"].create({"name": "Test Employee"})
        cls.timesheet = cls.env["account.analytic.line"].create(
            {
                "name": "Test Timesheet",
                "project_id": cls.project.id,
                "task_id": cls.task.id,
                "employee_id": cls.employee.id,
                "unit_amount": 1.0,
            }
        )

    def test_01_task_stage_id_reflects_task_stage(self):
        """task_stage_id on timesheet matches the task's current stage."""
        self.assertEqual(self.timesheet.task_stage_id, self.stage)

    def test_02_task_stage_id_updates_when_task_stage_changes(self):
        """task_stage_id updates when the related task stage changes."""
        new_stage = self.env["project.task.type"].create(
            {"name": "Done", "project_ids": [self.project.id]}
        )
        self.task.stage_id = new_stage
        self.timesheet.invalidate_recordset()
        self.assertEqual(self.timesheet.task_stage_id, new_stage)

    def test_03_task_stage_id_empty_when_no_task(self):
        """task_stage_id is empty when the timesheet has no linked task."""
        timesheet_no_task = self.env["account.analytic.line"].create(
            {
                "name": "No Task Timesheet",
                "project_id": self.project.id,
                "employee_id": self.employee.id,
                "unit_amount": 0.5,
            }
        )
        self.assertFalse(timesheet_no_task.task_stage_id)

    def test_04_task_stage_id_invisible_in_form_when_no_task(self):
        """task_stage_id statusbar is invisible in form view when no task is set."""
        timesheet_no_task = self.env["account.analytic.line"].create(
            {
                "name": "No Task Timesheet",
                "project_id": self.project.id,
                "employee_id": self.employee.id,
                "unit_amount": 0.5,
            }
        )
        view = "hr_timesheet_autofill.hr_timesheet_line_form_view"
        with Form(timesheet_no_task, view=view) as form:
            self.assertTrue(form._get_modifier("task_stage_id", "invisible"))

    def test_05_task_stage_id_visible_in_form_when_task_set(self):
        """task_stage_id statusbar is visible in form view when a task is linked."""
        view = "hr_timesheet_autofill.hr_timesheet_line_form_view"
        with Form(self.timesheet, view=view) as form:
            self.assertFalse(form._get_modifier("task_stage_id", "invisible"))
