# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Apr 2026

from lxml import etree

from odoo.addons.website.tools import MockRequest

from .common import TestHrTimesheetExcludeCommon


class TestHrTimesheetExclude(TestHrTimesheetExcludeCommon):
    """Tests for hr_timesheet_exclude module."""

    def _create_timesheet_line(self, project=None, task=None):
        """Create a timesheet analytic line for the given project and task."""
        return self.AnalyticLine.create(
            {
                "name": "Test Timesheet",
                "project_id": (project or self.project).id,
                "task_id": task.id if task else False,
                "employee_id": self.employee.id,
                "date": "2026-04-07",
                "unit_amount": 1.0,
            }
        )

    def test_01_posted_in_timesheet_default(self):
        """Check that posted_in_timesheet is True when no exclusion is set."""
        line = self._create_timesheet_line()
        self.assertTrue(line.posted_in_timesheet)

    def test_02_exclude_project(self):
        """Check that posted_in_timesheet is False when project is excluded."""
        self.project.exclude_from_timesheet = True
        line = self._create_timesheet_line()
        self.assertFalse(line.posted_in_timesheet)
        # reset
        self.project.exclude_from_timesheet = False

    def test_03_exclude_task(self):
        """Check that posted_in_timesheet is False when task is excluded."""
        self.task.exclude_from_timesheet = True
        line = self._create_timesheet_line(task=self.task)
        self.assertFalse(line.posted_in_timesheet)
        # reset
        self.task.exclude_from_timesheet = False

    def test_04_exclude_project_and_task(self):
        """Check that posted_in_timesheet is False when both project and task are
        excluded."""
        self.project.exclude_from_timesheet = True
        self.task.exclude_from_timesheet = True
        line = self._create_timesheet_line(task=self.task)
        self.assertFalse(line.posted_in_timesheet)
        # reset
        self.project.exclude_from_timesheet = False
        self.task.exclude_from_timesheet = False

    def test_05_recompute_on_project_change(self):
        """Check that posted_in_timesheet recomputes when project exclusion changes."""
        line = self._create_timesheet_line()
        self.assertTrue(line.posted_in_timesheet)
        self.project.exclude_from_timesheet = True
        self.assertFalse(line.posted_in_timesheet)
        self.project.exclude_from_timesheet = False
        self.assertTrue(line.posted_in_timesheet)

    def test_06_recompute_on_task_change(self):
        """Check that posted_in_timesheet recomputes when task exclusion changes."""
        line = self._create_timesheet_line(task=self.task)
        self.assertTrue(line.posted_in_timesheet)
        self.task.exclude_from_timesheet = True
        self.assertFalse(line.posted_in_timesheet)
        self.task.exclude_from_timesheet = False
        self.assertTrue(line.posted_in_timesheet)

    def test_07_project_form_view_fields(self):
        """Check that exclude_from_timesheet is present in the project form view."""
        with MockRequest(self.env) as mock:
            # simulate a debug HTTP request so base.group_no_one is active
            mock.session.debug = True
            self.assertTrue(self.env.user.has_group("base.group_no_one"))
            view_info = self.env["project.project"].get_view(view_type="form")
        arch = etree.fromstring(view_info["arch"].encode())
        field_names = [el.get("name") for el in arch.iter("field")]
        self.assertIn("exclude_from_timesheet", field_names)

    def test_08_task_form_view_fields(self):
        """Check that exclude_from_timesheet is present in the task form view."""
        with MockRequest(self.env) as mock:
            # simulate a debug HTTP request so base.group_no_one is active
            mock.session.debug = True
            self.assertTrue(self.env.user.has_group("base.group_no_one"))
            view_info = self.env["project.task"].get_view(view_type="form")
        arch = etree.fromstring(view_info["arch"].encode())
        field_names = [el.get("name") for el in arch.iter("field")]
        self.assertIn("exclude_from_timesheet", field_names)

    def test_09_analytic_line_search_view_fields(self):
        """Check that posted_in_timesheet filter is present in the search view."""
        view = self.env.ref("hr_timesheet_exclude.timesheet_search_view")
        view_info = self.env["account.analytic.line"].get_view(
            view_id=view.id, view_type="search"
        )
        arch = etree.fromstring(view_info["arch"].encode())
        filter_names = [el.get("name") for el in arch.iter("filter")]
        self.assertIn("filter_posted_in_timesheet", filter_names)

    def test_10_analytic_line_form_view_fields(self):
        """Check that exclude_from_sale_order is present in the analytic line form
        view."""
        view = self.env.ref("hr_timesheet_exclude.hr_timesheet_line_form_view")
        view_info = self.env["account.analytic.line"].get_view(
            view_id=view.id, view_type="form"
        )
        arch = etree.fromstring(view_info["arch"].encode())
        field_names = [el.get("name") for el in arch.iter("field")]
        self.assertIn("exclude_from_sale_order", field_names)
