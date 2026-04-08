# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Apr 2026

from odoo import Command
from odoo.tests.common import TransactionCase


class TestProjectTaskSubtaskCommon(TransactionCase):
    """Common base class with shared fixtures for project_task_subtask tests."""

    @classmethod
    def setUpClass(cls):
        """Set up shared test data."""
        super().setUpClass()
        group_project_user = cls.env.ref("project.group_project_user")
        cls.user_reviewer = cls.env["res.users"].create(
            {
                "name": "Test Reviewer",
                "login": "test_reviewer_subtask",
                "email": "reviewer@test.example.com",
                "groups_id": [Command.set([group_project_user.id])],
            }
        )
        cls.user_assignee = cls.env["res.users"].create(
            {
                "name": "Test Assignee",
                "login": "test_assignee_subtask",
                "email": "assignee@test.example.com",
                "groups_id": [Command.set([group_project_user.id])],
            }
        )
        cls.user_third = cls.env["res.users"].create(
            {
                "name": "Test Third Party",
                "login": "test_third_subtask",
                "email": "third@test.example.com",
                "groups_id": [Command.set([group_project_user.id])],
            }
        )
        cls.project = cls.env["project.project"].create(
            {
                "name": "Test Project for Subtasks",
            }
        )
        cls.task = cls.env["project.task"].create(
            {
                "name": "Test Task",
                "project_id": cls.project.id,
            }
        )
