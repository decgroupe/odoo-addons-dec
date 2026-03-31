# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Mar 2026

from datetime import date

from odoo.tests.common import TransactionCase

from odoo.addons.mail.tests.common import mail_new_test_user


class TestLeaveCalendarName(TransactionCase):
    """Tests for hr_leave_calendar_name module."""

    @classmethod
    def setUpClass(cls):
        """Set up shared test data."""
        super().setUpClass()
        cls.user_hrmanager = mail_new_test_user(
            cls.env,
            login="test_hrmanager",
            groups="base.group_user,hr_holidays.group_hr_holidays_manager",
        )
        cls.employee = cls.env["hr.employee"].create(
            {"name": "Test Employee", "user_id": cls.user_hrmanager.id}
        )
        cls.leave_type_day = cls.env["hr.leave.type"].create(
            {
                "name": "Test Day Leave",
                "requires_allocation": "no",
                "leave_validation_type": "no_validation",
                "create_calendar_meeting": True,
                "request_unit": "day",
            }
        )
        cls.leave_type_hour = cls.env["hr.leave.type"].create(
            {
                "name": "Test Hour Leave",
                "requires_allocation": "no",
                "leave_validation_type": "no_validation",
                "create_calendar_meeting": True,
                "request_unit": "hour",
            }
        )

    def _make_leave(self, leave_type, date_from, date_to):
        """Create and validate a leave request, returning the meeting."""
        leave = (
            self.env["hr.leave"]
            .with_context(mail_create_nolog=True, mail_notrack=True)
            .create(
                {
                    "employee_id": self.employee.id,
                    "holiday_status_id": leave_type.id,
                    "request_date_from": date_from,
                    "request_date_to": date_to,
                }
            )
        )
        leave.action_validate()
        return leave

    def test_01_custom_calendar_name_used_in_meeting(self):
        """When calendar_name is set on leave type, meeting name uses it."""
        self.leave_type_day.calendar_name = "Custom Meeting Label"
        leave = self._make_leave(
            self.leave_type_day,
            date(2025, 6, 2),
            date(2025, 6, 4),
        )
        self.assertTrue(leave.meeting_id, "A calendar meeting should have been created")
        self.assertIn(
            "Custom Meeting Label",
            leave.meeting_id.name,
            "Meeting name should contain the custom calendar_name",
        )
        self.assertIn(
            self.employee.name,
            leave.meeting_id.name,
            "Meeting name should contain the employee name",
        )

    def test_02_no_calendar_name_falls_back_to_display_name(self):
        """When calendar_name is not set, meeting name uses leave type display_name."""
        self.leave_type_day.calendar_name = False
        leave = self._make_leave(
            self.leave_type_day,
            date(2025, 7, 7),
            date(2025, 7, 9),
        )
        self.assertTrue(leave.meeting_id, "A calendar meeting should have been created")
        self.assertIn(
            self.leave_type_day.display_name,
            leave.meeting_id.name,
            "Meeting name should contain the leave type display_name",
        )
        self.assertIn(
            self.employee.name,
            leave.meeting_id.name,
            "Meeting name should contain the employee name",
        )

    def test_03_hour_based_leave_uses_hours_in_meeting_name(self):
        """For hour-based leave types, meeting name contains the number of hours."""
        self.leave_type_hour.calendar_name = "Hour Leave Label"
        leave = self._make_leave(
            self.leave_type_hour,
            date(2025, 8, 4),
            date(2025, 8, 4),
        )
        self.assertTrue(leave.meeting_id, "A calendar meeting should have been created")
        self.assertIn(
            "Hour Leave Label",
            leave.meeting_id.name,
            "Meeting name should contain the custom calendar_name",
        )
        # the unit string contains "hour"
        self.assertIn(
            "hour",
            leave.meeting_id.name.lower(),
            "Meeting name should contain an hour unit for hour-based leave",
        )

    def test_04_day_based_leave_uses_days_in_meeting_name(self):
        """For day-based leave types, meeting name contains the number of days."""
        self.leave_type_day.calendar_name = False
        leave = self._make_leave(
            self.leave_type_day,
            date(2025, 9, 1),
            date(2025, 9, 3),
        )
        self.assertTrue(leave.meeting_id, "A calendar meeting should have been created")
        # the unit string contains "day"
        self.assertIn(
            "day",
            leave.meeting_id.name.lower(),
            "Meeting name should contain a day unit for day-based leave",
        )
