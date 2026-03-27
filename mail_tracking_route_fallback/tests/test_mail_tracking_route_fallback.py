# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Mar 2026

from odoo.tests.common import TransactionCase


class TestMailTrackingRouteFallback(TransactionCase):
    """Tests for mail_tracking_route_fallback module."""

    @classmethod
    def setUpClass(cls):
        """Set up shared test data."""
        super().setUpClass()
        # create a partner to post a message on
        cls.partner = cls.env["res.partner"].create({"name": "Test Partner"})
        # post a message to get a mail.message with a proper message_id
        cls.message = cls.partner.message_post(
            body="Test message body",
            subject="Test Subject",
        )
        # create a tracking email linked to that message with a known token
        cls.tracking_email = cls.env["mail.tracking.email"].create(
            {
                "name": "Test Subject",
                "mail_message_id": cls.message.id,
                "token": "testtoken123",
                "recipient": "test@example.com",
                "sender": "sender@example.com",
            }
        )

    def _make_body_with_tracking_pixel(self, db, tracking_id, token):
        """Build an email body containing a tracking pixel URL."""
        return (
            '<html><body><img src="https://example.com/mail/tracking/open'
            f"/{db}/{tracking_id}/{token}/blank.gif"
            '" width="1" height="1"/></body></html>'
        )

    def test_01_get_message_id_from_tracking_data_match(self):
        """Return the linked message_id when db, id, and token all match."""
        db = self.env.cr.dbname
        body = self._make_body_with_tracking_pixel(
            db, self.tracking_email.id, self.tracking_email.token
        )
        message_dict = {"body": body}
        result = self.env["mail.thread"]._get_message_id_from_tracking_data(
            message_dict
        )
        self.assertEqual(result, self.message.message_id)

    def test_02_get_message_id_from_tracking_data_wrong_token(self):
        """Return False when the token does not match any tracking email."""
        db = self.env.cr.dbname
        body = self._make_body_with_tracking_pixel(
            db, self.tracking_email.id, "wrongtoken"
        )
        message_dict = {"body": body}
        result = self.env["mail.thread"]._get_message_id_from_tracking_data(
            message_dict
        )
        self.assertFalse(result)

    def test_03_get_message_id_from_tracking_data_wrong_db(self):
        """Return False when the db name in the URL does not match the current db."""
        body = self._make_body_with_tracking_pixel(
            "other_db", self.tracking_email.id, self.tracking_email.token
        )
        message_dict = {"body": body}
        result = self.env["mail.thread"]._get_message_id_from_tracking_data(
            message_dict
        )
        self.assertFalse(result)

    def test_04_get_message_id_from_tracking_data_no_pixel(self):
        """Return False when the email body contains no tracking pixel."""
        message_dict = {"body": "<html><body>No tracking pixel here.</body></html>"}
        result = self.env["mail.thread"]._get_message_id_from_tracking_data(
            message_dict
        )
        self.assertFalse(result)

    def test_05_message_route_get_thread_references_fallback(self):
        """Use tracking data as fallback when parent returns an empty reference."""
        db = self.env.cr.dbname
        body = self._make_body_with_tracking_pixel(
            db, self.tracking_email.id, self.tracking_email.token
        )
        message_dict = {"body": body}
        # pass None as `message` since the base implementation ignores it
        result = self.env["mail.thread"]._message_route_get_thread_references(
            None, message_dict
        )
        self.assertEqual(result, self.message.message_id)

    def test_06_message_route_get_thread_references_no_fallback_needed(self):
        """Return False when body has no pixel and parent also returns nothing."""
        message_dict = {"body": "<html><body>No tracking pixel here.</body></html>"}
        result = self.env["mail.thread"]._message_route_get_thread_references(
            None, message_dict
        )
        self.assertFalse(result)
