# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Sep 2023

from odoo.tests.common import TransactionCase


class TestProjectTimesheetProjectType(TransactionCase):
    """Tests for project_timesheet_project_type module."""

    @classmethod
    def setUpClass(cls):
        """Set up shared test fixtures."""
        super().setUpClass()
        cls.ProjectType = cls.env["project.type"]
        cls.Project = cls.env["project.project"]
        cls.Timesheet = cls.env["account.analytic.line"]
        cls.employee = cls.env["hr.employee"].create({"name": "Test Employee"})
        cls.project_type = cls.ProjectType.create({"name": "Internal"})
        cls.project = cls.Project.create(
            {
                "name": "Test Project",
                "type_id": cls.project_type.id,
            }
        )

    def test_01_project_type_id_populated_on_timesheet(self):
        """project_type_id is set on timesheet when project has a type."""
        line = self.Timesheet.create(
            {
                "name": "Work done",
                "project_id": self.project.id,
                "employee_id": self.employee.id,
            }
        )
        self.assertEqual(line.project_type_id, self.project_type)

    def test_02_project_type_id_empty_when_no_type(self):
        """project_type_id is empty on timesheet when project has no type."""
        project_no_type = self.Project.create({"name": "No Type Project"})
        line = self.Timesheet.create(
            {
                "name": "Other work",
                "project_id": project_no_type.id,
                "employee_id": self.employee.id,
            }
        )
        self.assertFalse(line.project_type_id)

    def test_03_project_type_id_updated_when_type_changes(self):
        """project_type_id is recomputed when the project type changes."""
        new_type = self.ProjectType.create({"name": "External"})
        line = self.Timesheet.create(
            {
                "name": "More work",
                "project_id": self.project.id,
                "employee_id": self.employee.id,
            }
        )
        self.assertEqual(line.project_type_id, self.project_type)
        self.project.type_id = new_type
        line.invalidate_recordset()
        self.assertEqual(line.project_type_id, new_type)
