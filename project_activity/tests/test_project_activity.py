# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Apr 2025

from odoo.tests.common import TransactionCase
from odoo import fields


class TestProjectActivity(TransactionCase):

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

    def test_01_create_task_without_activities(self):
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
        activity_type_ids = task_id.activity_ids.mapped("activity_type_id")
        self.assertNotIn(self.activity_to_assign, activity_type_ids)
        self.assertNotIn(self.activity_to_plan, activity_type_ids)

    def test_20_create_task_with_activities(self):
        # create task with no `user_id` and no `date_deadline`
        task_id = (
            self.env["project.task"]
            .with_context(auto_activity=True)
            .create(
                {
                    "name": "Test Task",
                    "project_id": self.project_rd_id.id,
                    # enforce empty `user_id` because `user_id` is set by default
                    # to env.user
                    "user_id": False,
                }
            )
        )
        activity_type_ids = task_id.activity_ids.mapped("activity_type_id")
        self.assertIn(self.activity_to_assign, activity_type_ids)
        self.assertIn(self.activity_to_plan, activity_type_ids)
        # create task with `user_id` but still no `date_deadline`
        task_id = (
            self.env["project.task"]
            .with_context(auto_activity=True)
            .create(
                {
                    "name": "Test Task",
                    "project_id": self.project_rd_id.id,
                    "user_id": self.env.user.id,
                }
            )
        )
        activity_type_ids = task_id.activity_ids.mapped("activity_type_id")
        self.assertNotIn(self.activity_to_assign, activity_type_ids)
        self.assertIn(self.activity_to_plan, activity_type_ids)
        # create task with `date_deadline` and `user_id`
        task_id = (
            self.env["project.task"]
            .with_context(auto_activity=True)
            .create(
                {
                    "name": "Test Task",
                    "project_id": self.project_rd_id.id,
                    "user_id": self.env.user.id,
                    "date_deadline": fields.Date.today(),
                }
            )
        )
        activity_type_ids = task_id.activity_ids.mapped("activity_type_id")
        self.assertNotIn(self.activity_to_assign, activity_type_ids)
        self.assertNotIn(self.activity_to_plan, activity_type_ids)

    def test_30_close_task_with_activities(self):
        # create task with no `user_id` and no `date_deadline`
        task_id = (
            self.env["project.task"]
            .with_context(auto_activity=True)
            .create(
                {
                    "name": "Test Task",
                    "project_id": self.project_rd_id.id,
                    # enforce empty `user_id` because `user_id` is set by default
                    # to env.user
                    "user_id": False,
                }
            )
        )
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
        # create task with no `user_id` and no `date_deadline`
        task_id = (
            self.env["project.task"]
            .with_context(auto_activity=True)
            .create(
                {
                    "name": "Test Task",
                    "project_id": self.project_rd_id.id,
                    # enforce empty `user_id` because `user_id` is set by default
                    # to env.user
                    "user_id": False,
                }
            )
        )
        activity_type_ids = task_id.activity_ids.mapped("activity_type_id")
        self.assertEqual(len(activity_type_ids), 2)
        task_id.action_assign_to_me()
        activity_type_ids = task_id.activity_ids.mapped("activity_type_id")
        self.assertEqual(len(activity_type_ids), 1)
        self.assertEqual(activity_type_ids, self.activity_to_plan)


    def test_50_task_post_assign_date(self):
        # create task with no `user_id` and no `date_deadline`
        task_id = (
            self.env["project.task"]
            .with_context(auto_activity=True)
            .create(
                {
                    "name": "Test Task",
                    "project_id": self.project_rd_id.id,
                    # enforce empty `user_id` because `user_id` is set by default
                    # to env.user
                    "user_id": False,
                }
            )
        )
        activity_type_ids = task_id.activity_ids.mapped("activity_type_id")
        self.assertEqual(len(activity_type_ids), 2)
        task_id.date_deadline = fields.Date.today()
        activity_type_ids = task_id.activity_ids.mapped("activity_type_id")
        self.assertEqual(len(activity_type_ids), 1)
        self.assertEqual(activity_type_ids, self.activity_to_assign)