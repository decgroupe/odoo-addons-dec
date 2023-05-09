# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, May 2023

from odoo.tests.common import TransactionCase


class TestProjectMerge(TransactionCase):
    """ """

    def setUp(self):
        super().setUp()
        self.project_model = self.env["project.project"]
        self.task_model = self.env["project.task"]
        self.merge_project_wizard_model = self.env["merge.project.project.wizard"]
        self.merge_task_wizard_model = self.env["merge.project.task.wizard"]
        self.group_do_merge = self.env.ref("project_merge.res_group_do_merge")

    def test_01_project_merge(self):
        project_1 = self.env.ref("project.project_project_1")
        project_2 = self.env.ref("project.project_project_2")
        # edit some values
        project_2.write({"description": "This is a project description"})
        # keep current data for future comparison
        project_1_data = project_1.read()[0]
        project_2_data = project_2.read()[0]
        # merge both projects
        wizard_id = self.merge_project_wizard_model.create(
            {
                "object_ids": (project_1 + project_2).ids,
                "dst_object_id": project_1.id,
            }
        )
        wizard_id.action_merge()
        self.assertTrue(project_1.exists())
        self.assertFalse(project_2.exists())
        project_1_new_data = project_1.read()[0]
        self.assertEqual(
            project_1_new_data["privacy_visibility"],
            project_1_data["privacy_visibility"],
        )
        self.assertEqual(
            project_1_new_data["description"],
            project_2_data["description"],
        )
        self.assertEqual(
            project_1_new_data["partner_id"],
            project_1_data["partner_id"],
        )
        self.assertEqual(
            project_1_new_data["task_count"],
            project_1_data["task_count"] + project_2_data["task_count"],
        )

    def test_02_task_merge(self):
        task_1 = self.env.ref("project.project_task_12")
        task_2 = self.env.ref("project.project_task_9")
        # edit some values
        task_2.write({"description": "This is a task description"})
        # keep current data for future comparison
        task_1_data = task_1.read()[0]
        task_2_data = task_2.read()[0]
        # merge both tasks
        wizard_id = self.merge_task_wizard_model.create(
            {
                "object_ids": (task_1 + task_2).ids,
                "dst_object_id": task_1.id,
            }
        )
        wizard_id.action_merge()
        self.assertTrue(task_1.exists())
        self.assertFalse(task_2.exists())
        task_1_new_data = task_1.read()[0]
        self.assertEqual(
            task_1_new_data["name"],
            task_1_data["name"],
        )
        self.assertEqual(
            task_1_new_data["description"],
            task_2_data["description"],
        )
        self.assertEqual(
            task_1_new_data["user_id"],
            task_1_data["user_id"],
        )
        self.assertNotEqual(
            task_1_new_data["user_id"],
            task_2_data["user_id"],
        )
        self.assertEqual(
            set(task_1_new_data["message_ids"]),
            set(task_1_data["message_ids"] + task_2_data["message_ids"]),
        )
