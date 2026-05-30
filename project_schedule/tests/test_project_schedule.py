# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, May 2026

from .common import TestProjectScheduleCommon


class TestProjectSchedule(TestProjectScheduleCommon):
    """Tests for project_schedule module."""

    def test_01_project_schedule_date_fields(self):
        """Project records must expose schedule mapping expected by mixin."""
        self._assert_schedule_fields(
            self.project_id,
            {
                "start": "date_start",
                "stop": "date",
                "deadline": "date",
            },
        )

    def test_02_project_schedulable_depends_on_active(self):
        """Inactive projects must not be considered schedulable."""
        self.project_id.active = False
        self.assertFalse(self.project_id.schedulable)
        self.project_id.active = True
        self.assertTrue(self.project_id.schedulable)

    def test_03_task_schedule_date_fields(self):
        """Task records must expose schedule mapping expected by mixin."""
        self._assert_schedule_fields(
            self.task_id,
            {
                "start": "date_assign",
                "stop": "date_end",
                "deadline": "date_deadline",
            },
        )
