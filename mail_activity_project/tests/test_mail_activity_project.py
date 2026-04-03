# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Apr 2026

from lxml import etree

from odoo.tests.common import TransactionCase


class TestMailActivityProject(TransactionCase):
    """Tests for mail_activity_project module."""

    @classmethod
    def setUpClass(cls):
        """Set up shared test data."""
        super().setUpClass()
        cls.Project = cls.env["project.project"]
        cls.Task = cls.env["project.task"]
        cls.MailActivity = cls.env["mail.activity"]
        cls.IrModel = cls.env["ir.model"]
        cls.activity_type = cls.env.ref("mail.mail_activity_data_todo")
        cls.project = cls.Project.create({"name": "Test Project"})
        cls.task = cls.Task.create(
            {
                "name": "Test Task",
                "project_id": cls.project.id,
            }
        )

    def test_01_compute_project_id_from_project(self):
        """An activity linked to a project record has project_id set to that project."""
        activity = self.MailActivity.create(
            {
                "res_model_id": self.IrModel._get("project.project").id,
                "res_id": self.project.id,
                "activity_type_id": self.activity_type.id,
                "user_id": self.env.user.id,
            }
        )
        self.assertEqual(activity.project_id, self.project)

    def test_02_compute_project_id_from_task(self):
        """An activity linked to a task inherits the project_id from the task."""
        activity = self.MailActivity.create(
            {
                "res_model_id": self.IrModel._get("project.task").id,
                "res_id": self.task.id,
                "activity_type_id": self.activity_type.id,
                "user_id": self.env.user.id,
            }
        )
        self.assertEqual(activity.project_id, self.project)

    def test_03_compute_project_id_no_project(self):
        """An activity linked to a model without project_id has project_id = False."""
        partner = self.env["res.partner"].create({"name": "Test Partner"})
        activity = self.MailActivity.create(
            {
                "res_model_id": self.IrModel._get("res.partner").id,
                "res_id": partner.id,
                "activity_type_id": self.activity_type.id,
                "user_id": self.env.user.id,
            }
        )
        self.assertFalse(activity.project_id)

    def test_04_activity_project_updated_on_task_write(self):
        """Writing a new project on a task propagates the change
        to linked activities."""
        activity = self.task.activity_schedule(
            activity_type_id=self.activity_type.id,
            user_id=self.env.user.id,
        )
        self.assertEqual(activity.project_id, self.project)
        new_project = self.Project.create({"name": "New Project"})
        self.task.write({"project_id": new_project.id})
        self.assertEqual(activity.project_id, new_project)

    def test_05_get_project_field_name(self):
        """_get_project_field_name returns 'project_id' for project.task."""
        self.assertEqual(self.task._get_project_field_name(), "project_id")

    def test_06_list_view_fields(self):
        """The project_id field is present in the combined activity list view arch."""
        view_info = self.MailActivity.get_view(view_type="list")
        arch = etree.fromstring(view_info["arch"])
        field_names = [el.get("name") for el in arch.iter("field")]
        self.assertIn("project_id", field_names)

    def test_07_search_view_fields(self):
        """The project_id field is present in the combined activity search view arch."""
        view_info = self.MailActivity.get_view(view_type="search")
        arch = etree.fromstring(view_info["arch"])
        field_names = [el.get("name") for el in arch.iter("field")]
        self.assertIn("project_id", field_names)
