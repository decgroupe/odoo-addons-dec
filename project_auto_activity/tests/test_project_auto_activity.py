# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Apr 2025

from odoo.addons.project_activity.tests.common import TestProjectActivityCommon


class TestProjectAutoActivity(TestProjectActivityCommon):

    def setUp(self):
        super().setUp()

    def test_01_create_task_without_activities(self):
        task_id = self._create_default_task()
        activity_type_ids = task_id.activity_ids.mapped("activity_type_id")
        self.assertNotIn(self.activity_to_assign, activity_type_ids)
        self.assertNotIn(self.activity_to_plan, activity_type_ids)

    def test_02_enforce_need_auto_activity(self):
        # override the `_need_auto_activity` method to always return True
        def need_auto_activity(self, vals):
            return True

        try:
            self.env["project.task"]._patch_method(
                "_need_auto_activity", need_auto_activity
            )
            task_id = self._create_default_task()
            activity_type_ids = task_id.activity_ids.mapped("activity_type_id")
            self.assertIn(self.activity_to_assign, activity_type_ids)
            self.assertIn(self.activity_to_plan, activity_type_ids)
        finally:
            # restore original method
            self.env["project.task"]._revert_method("_need_auto_activity")
