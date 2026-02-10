# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, May 2026

from odoo.tests.common import TransactionCase


class TestProjectMergeCommon(TransactionCase):
    """Common base class for project_merge tests."""

    @classmethod
    def setUpClass(cls):
        """Set up shared test data."""
        super().setUpClass()
        cls.project_model = cls.env["project.project"]
        cls.task_model = cls.env["project.task"]
        cls.merge_project_wizard_model = cls.env["merge.project.project.wizard"]
        cls.merge_task_wizard_model = cls.env["merge.project.task.wizard"]
        cls.group_do_merge = cls.env.ref("project_merge.res_group_do_merge")
