# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Mar 2026

import logging
from contextlib import contextmanager
from unittest.mock import patch

from odoo.tests.common import TransactionCase

from odoo.addons.mail.tests.common import mail_new_test_user

_test_logger = logging.getLogger("odoo.tests")


class TestMailDisableNotify(TransactionCase):
    """Tests for mail_disable_notify module."""

    @contextmanager
    def patch_mail_unlink(self):
        """Disable mail.mail.unlink so sent mails are kept for inspection."""

        def _disabled_unlink(self):
            _test_logger.warning("Unlink disabled for `mail.mail`")

        with patch.object(type(self.Mail), "unlink", _disabled_unlink):
            yield

    @classmethod
    def setUpClass(cls):
        """Set up shared test data."""
        super().setUpClass()
        cls.Mail = cls.env["mail.mail"]
        # create a user with inbox notification preference
        cls.user_inbox = mail_new_test_user(
            cls.env,
            login="test_inbox_user",
            name="Inbox User",
            groups="base.group_user",
            notification_type="inbox",
        )
        cls.partner_inbox = cls.user_inbox.partner_id
        # create a user with email notification preference
        cls.user_email = mail_new_test_user(
            cls.env,
            login="test_email_user",
            name="Email User",
            groups="base.group_user",
            notification_type="email",
        )
        cls.partner_email = cls.user_email.partner_id
        # use res.partner as the thread-enabled model for tests
        cls.record = cls.env["res.partner"].create({"name": "Test Partner Record"})

    def _get_inbox_notifs(self):
        """Return inbox notifications for this record's last message."""
        return (
            self.env["mail.notification"]
            .sudo()
            .search(
                [
                    ("mail_message_id.res_id", "=", self.record.id),
                    ("mail_message_id.model", "=", "res.partner"),
                    ("notification_type", "=", "inbox"),
                ]
            )
        )

    def _get_mail_mails(self):
        """Return outgoing mail.mail records for this record's last message."""
        return (
            self.env["mail.mail"]
            .sudo()
            .search(
                [
                    ("mail_message_id.res_id", "=", self.record.id),
                    ("mail_message_id.model", "=", "res.partner"),
                ]
            )
        )

    def test_01_normal_notification(self):
        """Verify inbox and email notifications are sent without context flags."""
        self.record.message_subscribe(
            partner_ids=[self.partner_inbox.id, self.partner_email.id]
        )
        notifs_before = self._get_inbox_notifs()
        with self.patch_mail_unlink():
            mails_before = self._get_mail_mails()
            self.record.message_post(
                body="Test message (normal)",
                partner_ids=[self.partner_inbox.id, self.partner_email.id],
            )
            notifs_after = self._get_inbox_notifs()
            mails_after = self._get_mail_mails()
            # inbox notification must have been created
            self.assertGreater(
                len(notifs_after - notifs_before),
                0,
                "Inbox notifications should be created without any disable flag",
            )
            # email notification must have been created
            self.assertGreater(
                len(mails_after - mails_before),
                0,
                "Email notifications should be created without any disable flag",
            )

    def test_02_disable_all_notifications(self):
        """mail_partner_notify_disable disables both inbox and email notifications."""
        self.record.message_subscribe(
            partner_ids=[self.partner_inbox.id, self.partner_email.id]
        )
        notifs_before = self._get_inbox_notifs()
        mails_before = self._get_mail_mails()
        self.record.with_context(mail_partner_notify_disable=True).message_post(
            body="Test message (all disabled)",
            partner_ids=[self.partner_inbox.id, self.partner_email.id],
        )
        notifs_after = self._get_inbox_notifs()
        mails_after = self._get_mail_mails()
        # no inbox notification must have been created
        self.assertEqual(
            len(notifs_after - notifs_before),
            0,
            "No inbox notifs expected when mail_partner_notify_disable is True",
        )
        # no email notification must have been created
        self.assertEqual(
            len(mails_after - mails_before),
            0,
            "No email notifs expected when mail_partner_notify_disable is True",
        )

    def test_03_disable_email_only(self):
        """mail_partner_notify_disable_email disables only email notifications."""
        self.record.message_subscribe(
            partner_ids=[self.partner_inbox.id, self.partner_email.id]
        )
        notifs_before = self._get_inbox_notifs()
        mails_before = self._get_mail_mails()
        self.record.with_context(mail_partner_notify_disable_email=True).message_post(
            body="Test message (email disabled)",
            partner_ids=[self.partner_inbox.id, self.partner_email.id],
        )
        notifs_after = self._get_inbox_notifs()
        mails_after = self._get_mail_mails()
        # inbox notification must still be created
        self.assertGreater(
            len(notifs_after - notifs_before),
            0,
            "Inbox notifications should still be created when only email is disabled",
        )
        # no email notification must have been created
        self.assertEqual(
            len(mails_after - mails_before),
            0,
            "No email notifs expected when mail_partner_notify_disable_email is True",
        )

    def test_04_disable_chat_only(self):
        """mail_partner_notify_disable_chat disables only inbox notifications."""
        self.record.message_subscribe(
            partner_ids=[self.partner_inbox.id, self.partner_email.id]
        )
        notifs_before = self._get_inbox_notifs()
        with self.patch_mail_unlink():
            mails_before = self._get_mail_mails()
            self.record.with_context(
                mail_partner_notify_disable_chat=True
            ).message_post(
                body="Test message (chat disabled)",
                partner_ids=[self.partner_inbox.id, self.partner_email.id],
            )
            notifs_after = self._get_inbox_notifs()
            mails_after = self._get_mail_mails()
            # no inbox notification must have been created
            self.assertEqual(
                len(notifs_after - notifs_before),
                0,
                "No inbox notifs when mail_partner_notify_disable_chat is set",
            )
            # email notification must still be created
            self.assertGreater(
                len(mails_after - mails_before),
                0,
                "Email notifs expected when only chat is disabled",
            )
