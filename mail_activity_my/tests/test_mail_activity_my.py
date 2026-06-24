# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, May 2026

from datetime import timedelta

from odoo import fields

from .common import TestMailActivityMyCommon


class TestMailActivityMy(TestMailActivityMyCommon):
    """Tests for mail_activity_my module."""

    def test_01_compute_state_planned(self):
        """activity_my_state is 'planned' when the next activity is in the future."""
        self._make_activity(self.record, self.user, days_from_today=7)
        self.record.invalidate_recordset()
        self.assertEqual(self.record.activity_my_state, "planned")

    def test_02_compute_state_today(self):
        """activity_my_state is 'today' when the next activity is due today."""
        self._make_activity(self.record, self.user, days_from_today=0)
        self.record.invalidate_recordset()
        self.assertEqual(self.record.activity_my_state, "today")

    def test_03_compute_state_overdue(self):
        """activity_my_state is 'overdue' when the next activity is past its
        deadline."""
        self._make_activity(self.record, self.user, days_from_today=-3)
        self.record.invalidate_recordset()
        self.assertEqual(self.record.activity_my_state, "overdue")

    def test_04_compute_state_no_activities(self):
        """activity_my_state is False when the record has no activities for the user."""
        self.record.invalidate_recordset()
        self.assertEqual(self.record.activity_my_state, False)

    def test_05_only_current_user_activities(self):
        """activity_my_ids only contains activities assigned to the current user."""
        act_mine = self._make_activity(self.record, self.user, days_from_today=5)
        act_other = self._make_activity(self.record, self.user2, days_from_today=3)
        self.record.invalidate_recordset()
        self.assertIn(act_mine, self.record.activity_my_ids)
        self.assertNotIn(act_other, self.record.activity_my_ids)

    def test_06_compute_fields_from_first_activity(self):
        """activity_my_type_id, activity_my_summary and activity_my_date_deadline
        reflect the first activity of the current user."""
        act = self._make_activity(self.record, self.user, days_from_today=2)
        act.write({"summary": "My test summary"})
        self.record.invalidate_recordset()
        self.assertEqual(self.record.activity_my_type_id, self.activity_type)
        self.assertEqual(self.record.activity_my_summary, "My test summary")
        self.assertEqual(self.record.activity_my_date_deadline, act.date_deadline)

    def test_07_action_snooze_future_deadline(self):
        """action_snooze_my postpones a future activity by 7 days."""
        act = self._make_activity(self.record, self.user, days_from_today=3)
        original_deadline = act.date_deadline
        self.record.action_snooze_my()
        self.assertEqual(act.date_deadline, original_deadline + timedelta(days=7))

    def test_08_action_snooze_overdue_deadline(self):
        """action_snooze_my reschedules an overdue activity to today + 7 days."""
        self._make_activity(self.record, self.user, days_from_today=-5)
        self.record.action_snooze_my()
        expected = fields.Date.today() + timedelta(days=7)
        act = self.record.activity_my_ids[:1]
        self.assertEqual(act.date_deadline, expected)

    def test_09_search_activity_my_date_deadline(self):
        """_search_activity_my_date_deadline returns records with matching deadline."""
        self._make_activity(self.record, self.user, days_from_today=10)
        deadline = fields.Date.today() + timedelta(days=10)
        result = self.TestModel.search([("activity_my_date_deadline", "=", deadline)])
        self.assertIn(self.record, result)

    def test_10_search_no_activities(self):
        """_search_activity_my_date_deadline returns records with no activities."""
        result = self.TestModel.search([("activity_my_date_deadline", "=", False)])
        self.assertIn(self.record, result)

    def test_11_compute_user_id_and_icon(self):
        """activity_my_user_id and activity_my_type_icon are computed from the
        first activity."""
        act = self._make_activity(self.record, self.user, days_from_today=1)
        self.record.invalidate_recordset()
        self.assertEqual(self.record.activity_my_user_id, self.user)
        self.assertEqual(self.record.activity_my_type_icon, act.activity_type_id.icon)

    def test_12_action_snooze_no_activity(self):
        """action_snooze_my returns True when there are no activities."""
        result = self.record.action_snooze_my()
        self.assertTrue(result)

    def test_13_read_group_by_activity_my_state(self):
        """_read_group_groupby supports grouping by activity_my_state."""
        self._make_activity(self.record, self.user, days_from_today=5)
        groups = self.TestModel._read_group(
            [],
            groupby=["activity_my_state"],
            aggregates=["__count"],
        )
        states = [g[0] for g in groups]
        self.assertIn("planned", states)
