# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, May 2026

from lxml import etree

from .common import TestProjectActivityMyCommon


class TestProjectActivityMy(TestProjectActivityMyCommon):
    """Tests for project_activity_my module."""

    def test_01_project_kanban_view_fields(self):
        """Check that mixin fields are present in the project kanban view."""
        view = self.env.ref("project_activity_my.view_project_kanban")
        view_info = self.env["project.project"].get_view(
            view_id=view.id, view_type="kanban"
        )
        arch = etree.fromstring(view_info["arch"])
        field_names = [el.get("name") for el in arch.iter("field")]
        self.assertIn("activity_my_ids", field_names)
        self.assertIn("activity_my_state", field_names)

    def test_02_task_list_view_fields(self):
        """Check that mixin fields are present in the task list view."""
        view = self.env.ref("project_activity_my.view_task_tree2")
        view_info = self.env["project.task"].get_view(view_id=view.id, view_type="list")
        arch = etree.fromstring(view_info["arch"])
        field_names = [el.get("name") for el in arch.iter("field")]
        self.assertIn("activity_my_ids", field_names)

    def test_03_project_activity_my_state_planned(self):
        """activity_my_state is 'planned' on project when the next activity is
        in the future."""
        self._make_activity(self.project, self.user, days_from_today=7)
        self.project.invalidate_recordset()
        self.assertEqual(self.project.activity_my_state, "planned")

    def test_04_project_activity_my_state_today(self):
        """activity_my_state is 'today' on project when the next activity is
        due today."""
        self._make_activity(self.project, self.user, days_from_today=0)
        self.project.invalidate_recordset()
        self.assertEqual(self.project.activity_my_state, "today")

    def test_05_project_activity_my_state_overdue(self):
        """activity_my_state is 'overdue' on project when the next activity is
        past its deadline."""
        self._make_activity(self.project, self.user, days_from_today=-3)
        self.project.invalidate_recordset()
        self.assertEqual(self.project.activity_my_state, "overdue")

    def test_06_project_activity_my_state_no_activities(self):
        """activity_my_state is False on project when there are no activities."""
        self.project.invalidate_recordset()
        self.assertEqual(self.project.activity_my_state, False)

    def test_07_project_only_current_user_activities(self):
        """activity_my_ids on project only contains activities assigned to the
        current user."""
        act_mine = self._make_activity(self.project, self.user, days_from_today=5)
        act_other = self._make_activity(self.project, self.user2, days_from_today=3)
        self.project.invalidate_recordset()
        self.assertIn(act_mine, self.project.activity_my_ids)
        self.assertNotIn(act_other, self.project.activity_my_ids)

    def test_08_task_activity_my_state_planned(self):
        """activity_my_state is 'planned' on task when the next activity is
        in the future."""
        self._make_activity(self.task, self.user, days_from_today=7)
        self.task.invalidate_recordset()
        self.assertEqual(self.task.activity_my_state, "planned")

    def test_09_task_activity_my_state_today(self):
        """activity_my_state is 'today' on task when the next activity is
        due today."""
        self._make_activity(self.task, self.user, days_from_today=0)
        self.task.invalidate_recordset()
        self.assertEqual(self.task.activity_my_state, "today")

    def test_10_task_activity_my_state_overdue(self):
        """activity_my_state is 'overdue' on task when the next activity is
        past its deadline."""
        self._make_activity(self.task, self.user, days_from_today=-3)
        self.task.invalidate_recordset()
        self.assertEqual(self.task.activity_my_state, "overdue")

    def test_11_task_activity_my_state_no_activities(self):
        """activity_my_state is False on task when there are no activities."""
        self.task.invalidate_recordset()
        self.assertEqual(self.task.activity_my_state, False)

    def test_12_task_only_current_user_activities(self):
        """activity_my_ids on task only contains activities assigned to the
        current user."""
        act_mine = self._make_activity(self.task, self.user, days_from_today=5)
        act_other = self._make_activity(self.task, self.user2, days_from_today=3)
        self.task.invalidate_recordset()
        self.assertIn(act_mine, self.task.activity_my_ids)
        self.assertNotIn(act_other, self.task.activity_my_ids)

    def test_13_progressbar_in_kanban(self):
        """Check that the progressbar element is present in the project kanban
        view."""
        view = self.env.ref("project_activity_my.view_project_kanban")
        view_info = self.env["project.project"].get_view(
            view_id=view.id, view_type="kanban"
        )
        arch = etree.fromstring(view_info["arch"])
        progressbars = arch.iter("progressbar")
        fields_with_progressbar = [pb.get("field") for pb in progressbars]
        self.assertIn("activity_my_state", fields_with_progressbar)
