# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Apr 2026

from datetime import date, datetime

from odoo import SUPERUSER_ID, Command
from odoo.tests.common import TransactionCase


class TestHrHolidaysTimesheetTimeControl(TransactionCase):
    """Tests for hr_holidays_timesheet_time_control module."""

    @classmethod
    def setUpClass(cls):
        """Set up shared test data."""
        super().setUpClass()
        # create a simple calendar in UTC timezone with Monday intervals
        # to have predictable work intervals regardless of server timezone
        cls.test_calendar = cls.env["resource.calendar"].create(
            {
                "name": "Test Monday Only (UTC)",
                "tz": "UTC",
                "attendance_ids": [
                    Command.create(
                        {
                            "name": "Monday Morning",
                            "dayofweek": "0",
                            "hour_from": 8.0,
                            "hour_to": 12.0,
                            "day_period": "morning",
                        }
                    ),
                    Command.create(
                        {
                            "name": "Monday Afternoon",
                            "dayofweek": "0",
                            "hour_from": 13.0,
                            "hour_to": 17.0,
                            "day_period": "afternoon",
                        }
                    ),
                ],
            }
        )
        cls.employee = cls.env["hr.employee"].create(
            {
                "name": "Test Employee",
                "resource_calendar_id": cls.test_calendar.id,
            }
        )
        # internal project and task are auto-created per company by
        # `project_timesheet_holidays`
        cls.project = cls.env.company.internal_project_id
        cls.task = cls.env.company.leave_timesheet_task_id
        cls.leave_type = cls.env["hr.leave.type"].create(
            {
                "name": "Test Leave (with timesheets)",
                "requires_allocation": "no",
                "leave_validation_type": "no_validation",
                "timesheet_generate": True,
                "timesheet_project_id": cls.project.id,
                "timesheet_task_id": cls.task.id,
                "request_unit": "day",
            }
        )
        cls.leave_type_no_ts = cls.env["hr.leave.type"].create(
            {
                "name": "Test Leave (no timesheets)",
                "requires_allocation": "no",
                "leave_validation_type": "no_validation",
                "time_type": "other",
                "request_unit": "day",
            }
        )

    def _create_leave(self, leave_type, date_from, date_to):
        """Create a leave request for the test employee using request date fields."""
        return (
            self.env["hr.leave"]
            .with_context(
                mail_create_nolog=True,
                mail_notrack=True,
                # warning: when fast create is not enabled, the `action_validate()`
                # is immediatly called on create.
                leave_fast_create=True,
            )
            .create(
                {
                    "employee_id": self.employee.id,
                    "holiday_status_id": leave_type.id,
                    "request_date_from": date_from,
                    "request_date_to": date_to,
                }
            )
        )

    def test_01_timesheets_created_with_date_time(self):
        """Leave validation creates timesheets with date_time set.

        For a single Monday leave with a morning+afternoon calendar, two
        timesheet lines should be generated (one per work interval), each
        with a non-null date_time that matches the interval start time.
        """
        # monday 2025-03-03: compute date_from/date_to via request_date_from/to
        leave = self._create_leave(
            self.leave_type,
            date(2025, 3, 3),
            date(2025, 3, 3),
        )
        self.assertEqual(leave.state, "confirm")
        leave.with_user(SUPERUSER_ID).action_validate()
        self.assertEqual(leave.state, "validate")
        # expect 2 intervals: morning (8-12) and afternoon (13-17) in UTC
        self.assertEqual(
            len(leave.timesheet_ids),
            2,
            "Expected 2 timesheets (one per work interval)",
        )
        for ts in leave.timesheet_ids:
            self.assertTrue(
                ts.date_time,
                f"Timesheet {ts.id} should have date_time set",
            )
        ts_sorted = leave.timesheet_ids.sorted(key=lambda r: r.date_time)
        # morning interval: 8:00-12:00 UTC = 4h
        self.assertAlmostEqual(ts_sorted[0].unit_amount, 4.0)
        self.assertEqual(ts_sorted[0].date_time, datetime(2025, 3, 3, 8, 0, 0))
        # afternoon interval: 13:00-17:00 UTC = 4h
        self.assertAlmostEqual(ts_sorted[1].unit_amount, 4.0)
        self.assertEqual(ts_sorted[1].date_time, datetime(2025, 3, 3, 13, 0, 0))

    def test_02_timesheets_use_project_and_task_from_leave_type(self):
        """Timesheets are linked to the project and task from the leave type."""
        leave = self._create_leave(
            self.leave_type,
            date(2025, 3, 3),
            date(2025, 3, 3),
        )
        self.assertEqual(leave.state, "confirm")
        leave.with_user(SUPERUSER_ID).action_validate()
        self.assertEqual(leave.state, "validate")
        self.assertTrue(leave.timesheet_ids)
        for ts in leave.timesheet_ids:
            self.assertEqual(ts.project_id, self.project)
            self.assertEqual(ts.task_id, self.task)
            self.assertEqual(ts.holiday_id, leave)

    def test_03_no_timesheets_when_generate_disabled(self):
        """No timesheets are created when the leave type has timesheet_generate
        disabled."""
        leave = self._create_leave(
            self.leave_type_no_ts,
            date(2025, 3, 3),
            date(2025, 3, 3),
        )
        self.assertEqual(leave.state, "confirm")
        leave.with_user(SUPERUSER_ID).action_validate()
        self.assertEqual(leave.state, "validate")
        self.assertFalse(
            leave.timesheet_ids,
            "No timesheets should be created when timesheet_generate is disabled",
        )
