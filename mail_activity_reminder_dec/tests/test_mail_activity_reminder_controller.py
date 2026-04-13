# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Apr 2026

import logging
from datetime import date

import odoo.tests

_logger = logging.getLogger(__name__)


@odoo.tests.tagged("post_install", "-at_install")
class TestMailActivityReminderDecController(odoo.tests.HttpCase):
    """HTTP controller tests for mail_activity_reminder_dec module."""

    def setUp(self):
        """Create a test activity and generate a fresh access token."""
        super().setUp()
        # establish a public session so the server can resolve auth="public" routes
        self.authenticate(None, None)
        self.test_user = self.env.ref("base.user_demo")
        self.test_partner = self.env.ref("base.partner_demo")
        self.activity_type = self.env.ref("mail.mail_activity_data_todo")
        self.activity = self.env["mail.activity"].create(
            {
                "activity_type_id": self.activity_type.id,
                "res_model_id": self.env["ir.model"]._get("res.partner").id,
                "res_id": self.test_partner.id,
                "user_id": self.test_user.id,
                "date_deadline": date.today(),
                "summary": "Controller test activity",
            }
        )
        self.test_user.generate_new_activity_reminder_access_token()
        self.token = self.test_user.activity_reminder_access_token

    def _api_action(self, activity, action, token, headers=False):
        if not headers:
            headers = {}
        resp = self.url_open(
            f"/api/reminder/v1/activity/{activity}/{action}?token={token}",
            headers=headers,
        )
        # self.assertEqual(resp.status_code, 200)
        return resp

    def _api_close(self, activity, token, headers=False):
        return self._api_action(
            activity=activity,
            action="close",
            token=token,
            headers=headers,
        )

    def _api_cancel(self, activity, token, headers=False):
        return self._api_action(
            activity=activity,
            action="cancel",
            token=token,
            headers=headers,
        )

    def _api_snooze(self, activity, snooze_value, snooze_unit, token, headers=False):
        action = f"snooze/{snooze_value}/{snooze_unit}"
        return self._api_action(
            activity=activity,
            action=action,
            token=token,
            headers=headers,
        )

    def test_01_close_valid_token(self):
        """Closing an activity via the endpoint with a valid token returns 200."""
        resp = self._api_close(
            activity=self.activity.id,
            token=self.token,
        )
        self.assertEqual(resp.status_code, 200)

    def test_02_cancel_valid_token(self):
        """Cancelling an activity via the endpoint with a valid token returns 200."""
        resp = self._api_cancel(
            activity=self.activity.id,
            token=self.token,
        )
        self.assertEqual(resp.status_code, 200)

    def test_03_snooze_valid_token(self):
        """Snoozing an activity via the endpoint with a valid token returns 200."""
        resp = self._api_snooze(
            activity=self.activity.id,
            snooze_value=1,
            snooze_unit="week",
            token=self.token,
        )
        self.assertEqual(resp.status_code, 200)

    def test_04_close_invalid_token(self):
        """Closing an activity with an invalid token returns the invalid-token page."""
        resp = self._api_close(
            activity=self.activity.id,
            token="bad-token",
        )
        self.assertEqual(resp.status_code, 200)
        self.assertIn(b"Invalid token", resp.content)

    def test_05_cancel_invalid_token(self):
        """Cancelling with an invalid token returns the invalid-token page."""
        resp = self._api_cancel(
            activity=self.activity.id,
            token="bad-token",
        )
        self.assertEqual(resp.status_code, 200)
        self.assertIn(b"Invalid token", resp.content)

    def test_20_snooze_invalid_token(self):
        """Snoozing with an invalid token returns the invalid-token page."""
        resp = self._api_snooze(
            activity=self.activity.id,
            snooze_value=1,
            snooze_unit="week",
            token="bad-token",
        )
        self.assertEqual(resp.status_code, 200)
        self.assertIn(b"Invalid token", resp.content)

    def test_21_close_activity_not_found(self):
        """Closing a deleted activity returns the not-found page."""
        activity_id = self.activity.id
        self.activity.unlink()
        resp = self._api_close(
            activity=activity_id,
            token=self.token,
        )
        self.assertEqual(resp.status_code, 200)
        self.assertIn(b"Activity not found", resp.content)
