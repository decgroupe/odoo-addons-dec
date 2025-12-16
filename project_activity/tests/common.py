# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Apr 2025

from odoo import Command
from odoo.tests.common import TransactionCase


class TestProjectActivityCommon(TransactionCase):
    def _create_default_task(self, vals=None, context=None):
        Task = self.env["project.task"]
        if context is not None:
            Task = Task.with_context(**context)
        # create task with no `user_ids`
        create_vals = {
            "name": "Test Task",
            "project_id": self.project_rd_id.id,
            # enforce empty `user_ids` because `user_ids` is set by default
            # to env.user
            "user_ids": [Command.set([])],
        }
        if vals is not None:
            create_vals.update(vals)
        task_id = Task.create(create_vals)
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
        # stages (task_state is set in demo file of project_task_stage_state)
        self.task_stage_new = self.env.ref("project.project_stage_0")
        self.task_stage_in_progress = self.env.ref("project.project_stage_1")
        self.assertEqual(self.task_stage_in_progress.task_state, "01_in_progress")
        self.task_stage_done = self.env.ref("project.project_stage_2")
        self.assertEqual(self.task_stage_done.task_state, "1_done")
        self.task_stage_cancelled = self.env.ref("project.project_stage_3")
        self.assertEqual(self.task_stage_cancelled.task_state, "1_canceled")
