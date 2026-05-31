# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, May 2026

from .common import TestMailActivityTeamScheduleCommon


class TestMailActivityTeamSchedule(TestMailActivityTeamScheduleCommon):
    """Tests for the mail_activity_team_schedule module."""

    def test_01_assigned_resource_uses_team_name_without_user(self):
        """Check assigned_resource falls back to team name when user is empty."""
        activity = self._create_activity({"user_id": False})
        self.assertFalse(activity.user_id)
        self.assertEqual(activity.assigned_resource, self.activity_team.name)

    def test_02_assigned_resource_keeps_user_name(self):
        """Check assigned_resource keeps user name when a user is assigned."""
        activity = self._create_activity({"user_id": False})
        activity.write({"user_id": self.env.user.id})
        self.assertEqual(activity.assigned_resource, self.env.user.name)
