# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Apr 2025

from odoo.tests.common import TransactionCase


class TestProjectActivityCommon(TransactionCase):

    def _create_default_task(self):
        # create task with no `user_id` and no `date_deadline`
        task_id = self.env["project.task"].create(
            {
                "name": "Test Task",
                "project_id": self.project_rd_id.id,
                # enforce empty `user_id` because `user_id` is set by default
                # to env.user
                "user_id": False,
            }
        )
        return task_id

    def setUp(self):
        super().setUp()
        # project references
        self.project_rd_id = self.env.ref("project.project_project_2")
        # activity types
        self.activity_to_assign = self.env.ref(
            "project_activity.mail_activity_to_assign"
        )
        self.activity_to_plan = self.env.ref("project_activity.mail_activity_to_plan")
        # stages
        self.task_stage_new = self.env.ref("project.project_stage_0")
        self.task_stage_in_progress = self.env.ref("project.project_stage_1")
        self.task_stage_done = self.env.ref("project.project_stage_2")
        self.task_stage_cancelled = self.env.ref("project.project_stage_3")
