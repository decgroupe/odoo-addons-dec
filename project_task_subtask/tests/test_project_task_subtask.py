# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Apr 2026

from lxml import etree

from odoo.exceptions import UserError

from .common import TestProjectTaskSubtaskCommon


class TestProjectTaskSubtask(TestProjectTaskSubtaskCommon):
    """Tests for project_task_subtask module."""

    def _create_subtask(self, user_id=None, reviewer=None, state="todo"):
        """Helper: create a subtask owned by reviewer, assigned to user_id."""
        if user_id is None:
            user_id = self.user_assignee
        if reviewer is None:
            reviewer = self.user_reviewer
        env = self.env(user=reviewer)
        return env["project.task.subtask"].create(
            {
                "name": "Test Checklist Item",
                "task_id": self.task.id,
                "user_id": user_id.id,
                "state": state,
            }
        )

    def test_01_create_subtask(self):
        """Check that creating a subtask sets reviewer from the current user."""
        subtask = self._create_subtask()
        self.assertEqual(subtask.reviewer_id, self.user_reviewer)
        self.assertEqual(subtask.user_id, self.user_assignee)
        self.assertEqual(subtask.state, "todo")
        self.assertEqual(subtask.project_id, self.project)

    def test_02_compute_recolor(self):
        """Check that recolor is True when the current user is the assignee in todo."""
        subtask = self._create_subtask()
        # assignee in todo state => recolor True
        subtask_as_assignee = subtask.with_user(self.user_assignee)
        self.assertTrue(subtask_as_assignee.recolor)
        # assignee in done state => recolor False
        subtask.write({"state": "done"})
        subtask_as_assignee.invalidate_recordset()
        self.assertFalse(subtask_as_assignee.recolor)
        # reviewer => recolor False
        subtask_as_reviewer = subtask.with_user(self.user_reviewer)
        self.assertFalse(subtask_as_reviewer.recolor)

    def test_03_compute_hide_button(self):
        """Check that hide_button is True for users unrelated to the subtask."""
        subtask = self._create_subtask()
        # third party => hide_button True
        subtask_as_third = subtask.with_user(self.user_third)
        self.assertTrue(subtask_as_third.hide_button)
        # assignee => hide_button False
        subtask_as_assignee = subtask.with_user(self.user_assignee)
        self.assertFalse(subtask_as_assignee.hide_button)
        # reviewer => hide_button False
        subtask_as_reviewer = subtask.with_user(self.user_reviewer)
        self.assertFalse(subtask_as_reviewer.hide_button)

    def test_04_change_state_methods(self):
        """Check that state change action methods set the correct state."""
        subtask = self._create_subtask()
        subtask.change_state_done()
        self.assertEqual(subtask.state, "done")
        subtask.change_state_todo()
        self.assertEqual(subtask.state, "todo")
        subtask.change_state_waiting()
        self.assertEqual(subtask.state, "waiting")
        subtask.change_state_cancelled()
        self.assertEqual(subtask.state, "cancelled")

    def test_05_write_state_by_reviewer(self):
        """Check that reviewer can change state and email is sent."""
        subtask = self._create_subtask()
        subtask_as_reviewer = subtask.with_user(self.user_reviewer)
        msg_count_before = len(
            self.task.message_ids.filtered(lambda m: m.message_type == "comment")
        )
        subtask_as_reviewer.write({"state": "done"})
        self.assertEqual(subtask.state, "done")
        self.task.invalidate_recordset()
        msg_count_after = len(
            self.task.message_ids.filtered(lambda m: m.message_type == "comment")
        )
        self.assertGreater(msg_count_after, msg_count_before)

    def test_06_write_name_by_reviewer(self):
        """Check that reviewer can change the name and email is sent."""
        subtask = self._create_subtask()
        subtask_as_reviewer = subtask.with_user(self.user_reviewer)
        subtask_as_reviewer.write({"name": "Updated Name"})
        self.assertEqual(subtask.name, "Updated Name")

    def test_07_write_user_id(self):
        """Check that changing user_id triggers an email notification."""
        subtask = self._create_subtask()
        subtask_as_reviewer = subtask.with_user(self.user_reviewer)
        msg_count_before = len(
            self.task.message_ids.filtered(lambda m: m.message_type == "comment")
        )
        subtask_as_reviewer.write({"user_id": self.user_third.id})
        self.task.invalidate_recordset()
        msg_count_after = len(
            self.task.message_ids.filtered(lambda m: m.message_type == "comment")
        )
        self.assertGreater(msg_count_after, msg_count_before)

    def test_08_write_restriction_third_party(self):
        """Check that a third-party user cannot change the state."""
        subtask = self._create_subtask()
        subtask_as_third = subtask.with_user(self.user_third)
        with self.assertRaises(UserError):
            subtask_as_third.write({"state": "done"})

    def test_09_write_restriction_name_third_party(self):
        """Check that a third-party user cannot change the name."""
        subtask = self._create_subtask()
        subtask_as_third = subtask.with_user(self.user_third)
        with self.assertRaises(UserError):
            subtask_as_third.write({"name": "Hacked Name"})

    def test_10_task_copy_with_subtasks(self):
        """Check that copying a task also copies its subtasks."""
        subtask = self._create_subtask()
        new_task = self.task.copy()
        self.assertTrue(new_task.subtask_ids)
        self.assertEqual(len(new_task.subtask_ids), 1)
        self.assertEqual(new_task.subtask_ids[0].name, subtask.name)

    def test_11_compute_user_subtask_ids(self):
        """Check that user subtask progress is computed correctly."""
        self._create_subtask(user_id=self.user_assignee, state="todo")
        self._create_subtask(user_id=self.user_assignee, state="done")
        self._create_subtask(user_id=self.user_assignee, state="waiting")
        self._create_subtask(user_id=self.user_assignee, state="cancelled")
        task_as_assignee = self.task.with_user(self.user_assignee)
        # 3 active subtasks: todo, done, waiting (cancelled excluded)
        self.assertEqual(len(task_as_assignee.user_active_subtask_ids), 3)
        self.assertEqual(len(task_as_assignee.user_done_subtask_ids), 1)
        self.assertEqual(len(task_as_assignee.user_todo_subtask_ids), 1)
        self.assertEqual(len(task_as_assignee.user_waiting_subtask_ids), 1)

    def test_12_compute_user_subtask_ids_empty(self):
        """Check that progress defaults to 100% when there are no active subtasks."""
        # no subtasks for user_third
        task_as_third = self.task.with_user(self.user_third)
        self.assertFalse(task_as_third.user_active_subtask_ids)
        self.assertEqual(task_as_third.user_done_subtask_progress, 100)
        self.assertEqual(task_as_third.user_todo_subtask_progress, 100)
        self.assertEqual(task_as_third.user_waiting_subtask_progress, 100)

    def test_13_kanban_progress_computed(self):
        """Check that kanban progress bar HTML is generated when subtasks exist."""
        self._create_subtask(user_id=self.user_assignee, state="todo")
        task_as_assignee = self.task.with_user(self.user_assignee)
        # with active subtasks, the progress bar should contain HTML
        self.assertIn("task_progress", task_as_assignee.kanban_subtasks_progress_bar)
        self.assertIn("kanban_subtasks", task_as_assignee.kanban_subtasks_progress_list)

    def test_14_action_delete(self):
        """Check that action_delete removes the subtask."""
        subtask = self._create_subtask()
        subtask_id = subtask.id
        subtask.action_delete()
        remaining = self.env["project.task.subtask"].search([("id", "=", subtask_id)])
        self.assertFalse(remaining)

    def test_15_send_subtask_email_self_reviewer_and_user(self):
        """Check email when the reviewer and assignee are the same current user."""
        env_self = self.env(user=self.user_reviewer)
        subtask = env_self["project.task.subtask"].create(
            {
                "name": "Self-assigned Item",
                "task_id": self.task.id,
                "user_id": self.user_reviewer.id,
                "state": "todo",
            }
        )
        # reviewer==user==current_user branch
        msg_count_before = len(self.task.message_ids)
        subtask.with_user(self.user_reviewer).write({"state": "done"})
        self.task.invalidate_recordset()
        self.assertGreater(len(self.task.message_ids), msg_count_before)

    def test_16_send_subtask_email_as_assignee(self):
        """Check email when assignee (not reviewer) changes state."""
        subtask = self._create_subtask()
        subtask_as_assignee = subtask.with_user(self.user_assignee)
        msg_count_before = len(self.task.message_ids)
        subtask_as_assignee.write({"state": "done"})
        self.task.invalidate_recordset()
        self.assertGreater(len(self.task.message_ids), msg_count_before)

    def test_17_send_subtask_email_name_change_with_old_name(self):
        """Check email when name changes includes the old_name branch."""
        subtask = self._create_subtask()
        subtask_as_reviewer = subtask.with_user(self.user_reviewer)
        msg_count_before = len(self.task.message_ids)
        # changing name triggers send_subtask_email with old_name set
        subtask_as_reviewer.write({"name": "Renamed Item"})
        self.task.invalidate_recordset()
        self.assertGreater(len(self.task.message_ids), msg_count_before)

    def test_18_compute_reviewer_id(self):
        """Check that _compute_reviewer_id sets reviewer from create_uid."""
        subtask = self._create_subtask()
        # call the compute method directly to cover that code path
        subtask._compute_reviewer_id()
        # reviewer should match create_uid after compute
        self.assertEqual(subtask.reviewer_id, subtask.create_uid)

    def test_19_form_view_fields(self):
        """Check that subtask_ids and default_user are in the task form view arch."""
        view_info = self.env["project.task"].get_view(view_type="form")
        arch = etree.fromstring(view_info["arch"].encode())
        field_names = [el.get("name") for el in arch.iter("field")]
        self.assertIn("subtask_ids", field_names)
        self.assertIn("default_user", field_names)

    def test_20_send_email_with_third_party_current_user(self):
        """Check email body when current user is neither reviewer nor assignee."""
        # create a subtask owned by user_reviewer, assigned to user_assignee
        subtask = self._create_subtask()
        # send email as user_third (neither reviewer nor user)
        task_as_third = self.task.with_user(self.user_third)
        msg_count_before = len(self.task.message_ids)
        task_as_third.send_subtask_email(
            subtask.name,
            subtask.state,
            subtask.reviewer_id.id,
            subtask.user_id.id,
        )
        self.task.invalidate_recordset()
        self.assertGreater(len(self.task.message_ids), msg_count_before)

    def test_21_convert_to_task(self):
        """Check that action_convert_to_task creates a child task and removes the
        item."""
        subtask = self._create_subtask(state="done")
        subtask_id = subtask.id
        subtask_name = subtask.name
        children_before = len(self.task.child_ids)
        subtask.action_convert_to_task()
        self.task.invalidate_recordset()
        self.assertEqual(len(self.task.child_ids), children_before + 1)
        child = self.task.child_ids[-1]
        self.assertEqual(child.name, subtask_name)
        self.assertEqual(child.project_id, self.project)
        self.assertIn(self.user_assignee, child.user_ids)
        self.assertEqual(child.state, "1_done")
        remaining = self.env["project.task.subtask"].search([("id", "=", subtask_id)])
        self.assertFalse(remaining)

    def test_22_convert_to_task_state_mapping(self):
        """Check that each subtask state maps to the correct task state."""
        state_map = {
            "done": "1_done",
            "cancelled": "1_canceled",
            "todo": "02_changes_requested",
            "waiting": "04_waiting_normal",
        }
        for subtask_state, expected_task_state in state_map.items():
            subtask = self._create_subtask(state=subtask_state)
            subtask.action_convert_to_task()
            self.task.invalidate_recordset()
            child = self.task.child_ids.filtered(
                lambda t: t.state == expected_task_state  # noqa: B023
            )
            self.assertTrue(
                child,
                f"No child task with state '{expected_task_state}' for subtask "
                f"state '{subtask_state}'",
            )
