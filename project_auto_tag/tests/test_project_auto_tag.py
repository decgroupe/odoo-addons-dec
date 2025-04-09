# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Apr 2025

from odoo.tests.common import TransactionCase


class TestProjectAutoTag(TransactionCase):

    def _create_default_task(self):
        # create task with no `user_id` and no `date_deadline`
        task_id = self.env["project.task"].create(
            {
                "name": "Test Task",
                "project_id": self.project_rd_id.id,
                "user_id": False,
            }
        )
        return task_id

    def setUp(self):
        super().setUp()
        # project references
        self.project_rd_id = self.env.ref("project.project_project_2")
        self.tag_bug_id = self.env.ref("project.project_tags_00")
        self.tag_feature_id = self.env.ref("project.project_tags_01")
        self.tag_experiment_id = self.env.ref("project.project_tags_02")
        self.tag_usability_id = self.env.ref("project.project_tags_03")

    def test_01_create_task_without_tags(self):
        task_id = self._create_default_task()
        self.assertFalse(task_id.tag_ids, "Task should not have any tags assigned")
        task_id.name = "Test Task without tags"
        self.assertFalse(task_id.tag_ids, "Task should still not have any tags assigned")

    def test_02_enforce_auto_tag(self):
        this = self
        # override the `_need_auto_tag` method to always return True
        def need_auto_tag(self, vals):
            return True

        try:
            self.env["project.task"]._patch_method("_need_auto_tag", need_auto_tag)
            task_id = self._create_default_task()
            self.assertFalse(task_id.tag_ids, "Task should not have any tags assigned")
        finally:
            # restore original methods
            self.env["project.task"]._revert_method("_need_auto_tag")

        # override the `_get_auto_tag_data` method to always return the same tag
        def get_auto_tag_data(self):
            # call the original method
            origin, tag_id = self.env["project.task"]._get_auto_tag_data.origin(self)
            # set a custom tag
            tag_id = this.tag_bug_id
            return origin, tag_id

        try:
            self.env["project.task"]._patch_method("_need_auto_tag", need_auto_tag)
            self.env["project.task"]._patch_method(
                "_get_auto_tag_data", get_auto_tag_data
            )
            task_id = self._create_default_task()
            self.assertEqual(
                task_id.tag_ids,
                self.tag_bug_id,
                "'Bug' tag should be assigned",
            )
        finally:
            # restore original methods
            self.env["project.task"]._revert_method("_need_auto_tag")
            self.env["project.task"]._revert_method("_get_auto_tag_data")
