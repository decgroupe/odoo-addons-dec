# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Apr 2025

from odoo import Command, fields

from .common import TestProjectActivityCommon


class TestProjectActivity(TestProjectActivityCommon):
    def test_01_create_task_without_activities(self):
        task_id = self._create_default_task()
        activity_type_ids = task_id.activity_ids.mapped("activity_type_id")
        self.assertNotIn(self.activity_to_assign, activity_type_ids)
        self.assertNotIn(self.activity_to_plan, activity_type_ids)

    def test_20_create_task_with_activities(self):
        # create task with no `user_ids` and no `date_deadline`
        task_id = (
            self.env["project.task"]
            .with_context(auto_activity=True)
            .create(
                {
                    "name": "Test Task",
                    "project_id": self.project_rd_id.id,
                    # enforce empty `user_ids` because `user_ids` is set by default
                    # to env.user
                    "user_ids": [],
                }
            )
        )
        activity_type_ids = task_id.activity_ids.mapped("activity_type_id")
        self.assertIn(self.activity_to_assign, activity_type_ids)
        self.assertIn(self.activity_to_plan, activity_type_ids)
        # create task with `user_ids` but still no `date_deadline`
        task_id = self._create_default_task(
            vals={
                "user_ids": [Command.set([self.env.user.id])],
            },
            context={"auto_activity": True},
        )
        activity_type_ids = task_id.activity_ids.mapped("activity_type_id")
        self.assertNotIn(self.activity_to_assign, activity_type_ids)
        self.assertIn(self.activity_to_plan, activity_type_ids)
        # create task with `date_deadline` and `user_ids`
        task_id = self._create_default_task(
            vals={
                "user_ids": [Command.set([self.env.user.id])],
                "date_deadline": fields.Date.today(),
            },
            context={"auto_activity": True},
        )
        activity_type_ids = task_id.activity_ids.mapped("activity_type_id")
        self.assertNotIn(self.activity_to_assign, activity_type_ids)
        self.assertNotIn(self.activity_to_plan, activity_type_ids)

    def test_30_close_task_with_activities(self):
        task_id = self._create_default_task(context={"auto_activity": True})
        activity_type_ids = task_id.activity_ids.mapped("activity_type_id")
        self.assertEqual(len(activity_type_ids), 2)
        # check that nothing has changed when using a non-closed stage
        task_id.write({"stage_id": self.task_stage_in_progress.id})
        activity_type_ids = task_id.activity_ids.mapped("activity_type_id")
        self.assertEqual(len(activity_type_ids), 2)
        # set the task to "done" and check that the activities are removed
        task_id.write({"stage_id": self.task_stage_done.id})
        activity_type_ids = task_id.activity_ids.mapped("activity_type_id")
        self.assertEqual(len(activity_type_ids), 0)

    def test_40_task_post_assign_user(self):
        task_id = self._create_default_task(context={"auto_activity": True})
        activity_type_ids = task_id.activity_ids.mapped("activity_type_id")
        self.assertEqual(len(activity_type_ids), 2)
        task_id.user_ids = [Command.link(self.env.user.id)]  # action_assign_to_me
        activity_type_ids = task_id.activity_ids.mapped("activity_type_id")
        self.assertEqual(len(activity_type_ids), 1)
        self.assertEqual(activity_type_ids, self.activity_to_plan)

    def test_50_task_post_assign_date(self):
        task_id = self._create_default_task(context={"auto_activity": True})
        activity_type_ids = task_id.activity_ids.mapped("activity_type_id")
        self.assertEqual(len(activity_type_ids), 2)
        task_id.date_deadline = fields.Date.today()
        activity_type_ids = task_id.activity_ids.mapped("activity_type_id")
        self.assertEqual(len(activity_type_ids), 1)
        self.assertEqual(activity_type_ids, self.activity_to_assign)
