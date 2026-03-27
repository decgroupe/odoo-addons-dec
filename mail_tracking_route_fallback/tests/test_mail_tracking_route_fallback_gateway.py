# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Mar 2026

from odoo.tests.common import TransactionCase
from odoo.tools import mute_logger

from odoo.addons.mail.tests.common import MailCase
from odoo.addons.mail_tracking_route_fallback.tests.common import (
    MSG_TRACKING_REPLY_TEMPLATE,
)


class TestMailTrackingRouteFallbackRealFlow(TransactionCase, MailCase):
    """End-to-end gateway tests for mail_tracking_route_fallback module."""

    @classmethod
    def setUpClass(cls):
        """Set up shared test data including alias domain and tracking email."""
        super().setUpClass()
        # create company default alias domain required for catchall routing
        cls.env["mail.alias.domain"].create(
            {
                "name": "yourcompany.com",
                "bounce_alias": "bounce",
                "catchall_alias": "catchall",
            }
        )
        # create a partner to use as the mail.thread target
        cls.partner = cls.env["res.partner"].create({"name": "Test Partner"})
        # post a message to get a mail.message with a real message_id
        cls.message = cls.partner.message_post(
            body="Notification body",
            subject="Test notification",
        )
        # create a tracking email linked to that message with a known token
        cls.tracking_email = cls.env["mail.tracking.email"].create(
            {
                "name": "Test notification",
                "mail_message_id": cls.message.id,
                "token": "gatewaytoken456",
                "recipient": "sender@example.com",
                "sender": "noreply@yourcompany.com",
            }
        )

    def _build_incoming_email(self, unique_id, token=None, db=None):
        """Format MSG_TRACKING_REPLY_TEMPLATE with real ids for gateway tests."""
        return MSG_TRACKING_REPLY_TEMPLATE.format(
            unique_id=unique_id,
            db=db if db is not None else self.env.cr.dbname,
            tracking_id=self.tracking_email.id,
            token=token if token is not None else self.tracking_email.token,
        )

    @mute_logger("odoo.addons.mail.models.mail_thread")
    def test_01_reply_routed_via_tracking_pixel(self):
        """Incoming email with no thread headers is routed via tracking pixel."""
        incoming_message = self._build_incoming_email(unique_id="test01")
        prev_msg_ids = self.partner.message_ids
        record_id = self.env["mail.thread"].message_process(None, incoming_message)
        new_msgs = self.partner.message_ids - prev_msg_ids
        self.assertEqual(1, len(new_msgs))
        self.assertEqual(self.partner.id, record_id)

    @mute_logger("odoo.addons.mail.models.mail_thread")
    def test_02_reply_not_routed_with_wrong_token(self):
        """Incoming email with a wrong token in the pixel is not routed."""
        incoming_message = self._build_incoming_email(
            unique_id="test02", token="wrongtoken"
        )
        prev_msg_ids = self.partner.message_ids
        # message_process returns False when no thread is found
        record_id = self.env["mail.thread"].message_process(None, incoming_message)
        new_msgs = self.partner.message_ids - prev_msg_ids
        self.assertEqual(0, len(new_msgs))
        self.assertFalse(record_id)

    @mute_logger("odoo.addons.mail.models.mail_thread")
    def test_03_reply_not_routed_with_wrong_db(self):
        """Incoming email with a wrong db name in the pixel is not routed."""
        incoming_message = self._build_incoming_email(unique_id="test03", db="other_db")
        prev_msg_ids = self.partner.message_ids
        record_id = self.env["mail.thread"].message_process(None, incoming_message)
        new_msgs = self.partner.message_ids - prev_msg_ids
        self.assertEqual(0, len(new_msgs))
        self.assertFalse(record_id)
