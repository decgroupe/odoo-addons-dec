# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Apr 2026

import logging
from contextlib import contextmanager
from datetime import date, timedelta
from unittest.mock import patch

from odoo import fields
from odoo.exceptions import UserError

from .common import TestMailActivityReminderDecCommon

_test_logger = logging.getLogger("odoo.tests")


class TestMailActivityReminderDec(TestMailActivityReminderDecCommon):
    """Tests for mail_activity_reminder_dec module."""

    @contextmanager
    def patch_mail_unlink(self):
        """Disable mail.mail.unlink so sent mails are kept for inspection."""
        Mail = self.env["mail.mail"]
        _origin = type(Mail).unlink

        def _disabled_unlink(self):
            _test_logger.warning("Unlink disabled for `mail.mail`")

        with patch.object(type(Mail), "unlink", _disabled_unlink):
            yield

    def test_01_action_snooze_day(self):
        """Snoozing by day extends the deadline by N days."""
        original_deadline = self.activity.date_deadline
        self.activity.action_snooze("day", 3)
        expected = original_deadline + timedelta(days=3)
        self.assertEqual(self.activity.date_deadline, expected)

    def test_02_action_snooze_week(self):
        """Snoozing by week extends the deadline by N weeks."""
        original_deadline = self.activity.date_deadline
        self.activity.action_snooze("week", 1)
        expected = original_deadline + timedelta(weeks=1)
        self.assertEqual(self.activity.date_deadline, expected)

    def test_03_action_snooze_month(self):
        """Snoozing by month extends the deadline by N months."""
        # use a future deadline so snooze is computed from that date
        self.activity.write({"date_deadline": date(2026, 5, 15)})
        self.activity.action_snooze("month", 1)
        self.assertEqual(self.activity.date_deadline, date(2026, 6, 15))

    def test_04_action_snooze_year(self):
        """Snoozing by year extends the deadline by N years."""
        # use a future deadline so snooze is computed from that date
        self.activity.write({"date_deadline": date(2026, 7, 1)})
        self.activity.action_snooze("year", 1)
        self.assertEqual(self.activity.date_deadline, date(2027, 7, 1))

    def test_05_action_snooze_invalid_unit(self):
        """Snoozing with an invalid unit raises a UserError."""
        with self.assertRaises(UserError):
            self.activity.action_snooze("invalid", 1)

    def test_06_action_snooze_from_date(self):
        """Snoozing from a past date extends from that date instead of deadline."""
        from_date = fields.Date.to_date("2025-01-01")
        self.activity.action_snooze("day", 7, from_date=from_date)
        expected = from_date + timedelta(days=7)
        # if from_date is in the past, snooze starts from today
        today = date.today()
        if from_date < today:
            expected = today + timedelta(days=7)
        self.assertEqual(self.activity.date_deadline, expected)

    def test_07_get_group_activity_ids_groups_by_type(self):
        """_get_group_activity_ids returns activities grouped by activity type."""
        group = self.test_user._get_group_activity_ids(
            [("res_model", "=", "res.partner")],
            order="date_deadline asc",
        )
        self.assertIn(self.activity_type, group)
        self.assertIn(self.activity, group[self.activity_type])

    def test_08_get_group_activity_ids_empty_domain(self):
        """_get_group_activity_ids returns nothing for a never-matching domain."""
        group = self.test_user._get_group_activity_ids(
            [("id", "=", -1)],
            order="date_deadline asc",
        )
        self.assertEqual(len(group), 0)

    def test_09_send_activity_reminder_sends_email(self):
        """send_activity_reminder sends an email when the user has activities."""
        # ensure the user has an email
        self.test_user.partner_id.email = "demo@example.com"
        self.test_user.generate_new_activity_reminder_access_token()
        with self.patch_mail_unlink():
            self.test_user.send_activity_reminder()
            mail = self.env["mail.mail"].search(
                [("email_to", "=", self.test_user.email_formatted)], limit=1
            )
            self.assertTrue(mail, "A reminder mail should have been created")

    def test_10_send_activity_reminder_no_activities(self):
        """send_activity_reminder does not send email when user has no activities."""
        # create a user with no activities
        partner = self.env["res.partner"].create({"name": "No Activity User"})
        user = self.env["res.users"].create(
            {
                "name": "No Activity User",
                "login": "no_activity_user_test",
                "partner_id": partner.id,
                "email": "no_activity@example.com",
            }
        )
        with self.patch_mail_unlink():
            user.send_activity_reminder()
            mail = self.env["mail.mail"].search(
                [("email_to", "=", user.email_formatted)], limit=1
            )
            self.assertFalse(mail, "No mail should be sent if user has no activities")

    def test_11_generate_new_activity_reminder_access_token(self):
        """Generating a new token produces a non-empty UUID string."""
        self.test_user.generate_new_activity_reminder_access_token()
        token = self.test_user.activity_reminder_access_token
        self.assertTrue(token)
        self.assertEqual(len(token), 36, "token should be a UUID (36 chars)")

    def test_12_form_view_fields(self):
        """Check that the send_activity_reminder button is present in res.users form."""
        from lxml import etree

        parent_view = self.env.ref("base.view_users_form")
        view_info = self.env["res.users"].get_view(
            view_id=parent_view.id, view_type="form"
        )
        arch = etree.fromstring(view_info["arch"])
        button_names = [el.get("name") for el in arch.iter("button")]
        self.assertIn("send_activity_reminder", button_names)

    def test_13_action_snooze_with_plain_note(self):
        """Snoozing appends a notification text to an existing non-p note."""
        self.activity.write({"note": "<div>existing note</div>"})
        original_deadline = self.activity.date_deadline
        self.activity.action_snooze("day", 1)
        expected = original_deadline + timedelta(days=1)
        self.assertEqual(self.activity.date_deadline, expected)
        self.assertIn("Deadline extended", self.activity.note or "")

    def test_14_action_snooze_with_p_note(self):
        """Snoozing inserts a notification before a <p> note element."""
        self.activity.write({"note": "<p>original note</p>"})
        original_deadline = self.activity.date_deadline
        self.activity.action_snooze("week", 1)
        expected = original_deadline + timedelta(weeks=1)
        self.assertEqual(self.activity.date_deadline, expected)
        self.assertIsNotNone(self.activity.note)
