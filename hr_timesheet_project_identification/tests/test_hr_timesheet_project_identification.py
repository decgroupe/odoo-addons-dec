# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Mar 2026

from odoo.tests.common import TransactionCase


class TestHrTimesheetProjectIdentification(TransactionCase):
    """Tests for hr_timesheet_project_identification module."""

    @classmethod
    def setUpClass(cls):
        """Set up shared test data."""
        super().setUpClass()
        cls.model_analytic_line = cls.env["account.analytic.line"]
        cls.model_project = cls.env["project.project"]
        cls.ptype_contract = cls.env.ref("project_identification.contract_type")
        cls.employee = cls.env["hr.employee"].create({"name": "Test Employee"})
        cls.project_no_type = cls.model_project.create({"name": "Project A"})
        cls.project_with_type = cls.model_project.create(
            {
                "name": "Project B",
                "type_id": cls.ptype_contract.id,
            }
        )

    def _create_timesheet_line(self, project=None):
        """Create a timesheet line optionally linked to a project."""
        vals = {
            "name": "Test timesheet",
            "date": "2026-03-30",
            "employee_id": self.employee.id,
        }
        if project:
            vals["project_id"] = project.id
        return self.model_analytic_line.create(vals)

    def test_01_no_project_gives_false(self):
        """A timesheet line without a project has a False identification."""
        line = self._create_timesheet_line()
        self.assertFalse(line.project_identification)

    def test_02_project_without_type(self):
        """A timesheet line linked to a project with no type shows the project name."""
        line = self._create_timesheet_line(project=self.project_no_type)
        self.assertEqual(line.project_identification, "Project A")

    def test_03_project_with_type(self):
        """A timesheet line linked to a project with a type shows name and type."""
        line = self._create_timesheet_line(project=self.project_with_type)
        # project_identification is built by joining _get_name_identifications()
        expected = " / ".join(self.project_with_type._get_name_identifications())
        self.assertEqual(line.project_identification, expected)
        self.assertIn("Project B", line.project_identification)

    def test_04_project_change_updates_identification(self):
        """Changing the project on a timesheet line recomputes the identification."""
        line = self._create_timesheet_line()
        self.assertFalse(line.project_identification)
        line.project_id = self.project_no_type
        self.assertEqual(line.project_identification, "Project A")
        line.project_id = False
        self.assertFalse(line.project_identification)
