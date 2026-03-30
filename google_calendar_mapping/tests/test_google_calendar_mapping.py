# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Mar 2026

from datetime import datetime

from odoo.tests.common import TransactionCase

from odoo.addons.google_calendar.utils.google_event import GoogleEvent


class TestGoogleCalendarMapping(TransactionCase):
    """Tests for google_calendar_mapping module."""

    @classmethod
    def setUpClass(cls):
        """Set up shared test data."""
        super().setUpClass()
        # create a user whose Odoo email differs from their Google Calendar ID
        cls.mapped_user = cls.env["res.users"].create(
            {
                "name": "Mapped User",
                "login": "mapped_user@odoo.test",
                "email": "mapped_user@odoo.test",
                "groups_id": [
                    (4, cls.env.ref("base.group_user").id),
                ],
            }
        )
        # store the settings record for easier access
        cls.mapped_user_settings = cls.env[
            "res.users.settings"
        ]._find_or_create_for_user(cls.mapped_user)
        # set the google calendar ID (requires sudo because of group restriction)
        cls.mapped_user_settings.sudo().write(
            {"google_calendar_cal_id": "mapped_user@google.test"}
        )

    def _make_google_event(self, attendee_emails):
        """Build a minimal GoogleEvent dict for testing."""
        return GoogleEvent(
            [
                {
                    "id": "test-event-google-id",
                    "summary": "Test Event",
                    "organizer": {"email": self.env.user.email},
                    "attendees": [
                        {"email": email, "responseStatus": "accepted"}
                        for email in attendee_emails
                    ],
                    "reminders": {"useDefault": False, "overrides": []},
                    "start": {"dateTime": "2026-03-30T09:00:00Z"},
                    "end": {"dateTime": "2026-03-30T10:00:00Z"},
                }
            ]
        )

    def test_01_incoming_google_email_is_replaced(self):
        """Attendee with google_calendar_cal_id maps to Odoo email on incoming."""
        google_event = self._make_google_event(["mapped_user@google.test"])
        # call as admin so field accesses work
        CalendarEvent = self.env["calendar.event"].sudo()
        attendee_cmds, partner_cmds = CalendarEvent._odoo_attendee_commands(
            google_event
        )
        # the partner command should reference the mapped user's partner
        partner_ids_in_cmds = [cmd[1] for cmd in partner_cmds if cmd[0] == 4]
        self.assertIn(
            self.mapped_user.partner_id.id,
            partner_ids_in_cmds,
            "partner_commands should link the mapped user's partner when their "
            "google_calendar_cal_id matches the attendee email",
        )

    def test_02_incoming_unknown_google_email_is_unchanged(self):
        """Attendee email without a matching user is left untouched on incoming."""
        unknown_email = "unknown@google.test"
        google_event = self._make_google_event([unknown_email])
        CalendarEvent = self.env["calendar.event"].sudo()
        attendee_cmds, partner_cmds = CalendarEvent._odoo_attendee_commands(
            google_event
        )
        # no attendee command should reference the mapped user
        partner_ids_in_cmds = [cmd[1] for cmd in partner_cmds if cmd[0] == 4]
        self.assertNotIn(
            self.mapped_user.partner_id.id,
            partner_ids_in_cmds,
            "mapped user's partner should not appear when their google_calendar_cal_id "
            "does not match the attendee email",
        )

    def test_03_outgoing_odoo_email_is_replaced_for_attendee(self):
        """Attendee Odoo email is replaced with google_calendar_cal_id on outgoing."""
        # create a calendar event with the mapped user as attendee
        event = (
            self.env["calendar.event"]
            .sudo()
            .create(
                {
                    "name": "Test Outgoing Event",
                    "start": datetime(2026, 3, 30, 9, 0, 0),
                    "stop": datetime(2026, 3, 30, 10, 0, 0),
                    "partner_ids": [(4, self.mapped_user.partner_id.id)],
                    "need_sync": False,
                }
            )
        )
        values = event.with_user(self.env.user)._google_values()
        attendee_emails = [a["email"] for a in values.get("attendees", [])]
        self.assertIn(
            "mapped_user@google.test",
            attendee_emails,
            "outgoing attendee email should be replaced with google_calendar_cal_id",
        )
        self.assertNotIn(
            "mapped_user@odoo.test",
            attendee_emails,
            "outgoing attendee email should not contain the Odoo email when a "
            "google_calendar_cal_id is set",
        )

    def test_04_outgoing_odoo_email_is_replaced_for_organizer(self):
        """Organizer Odoo email is replaced with google_calendar_cal_id on outgoing."""
        # create a calendar event organized by the mapped user
        event = (
            self.env["calendar.event"]
            .with_user(self.mapped_user)
            .create(
                {
                    "name": "Test Organizer Event",
                    "start": datetime(2026, 3, 30, 9, 0, 0),
                    "stop": datetime(2026, 3, 30, 10, 0, 0),
                    "need_sync": False,
                }
            )
        )
        values = event.with_user(self.mapped_user)._google_values()
        organizer = values.get("organizer", {})
        self.assertEqual(
            organizer.get("email"),
            "mapped_user@google.test",
            "outgoing organizer email should be replaced with google_calendar_cal_id",
        )
