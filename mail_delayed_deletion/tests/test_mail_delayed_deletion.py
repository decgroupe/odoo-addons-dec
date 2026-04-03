# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Apr 2026

import logging
from datetime import datetime, timedelta

from odoo.tests.common import TransactionCase

_test_logger = logging.getLogger("odoo.tests")


class TestMailDelayedDeletion(TransactionCase):
    """Tests for mail_delayed_deletion module."""

    @classmethod
    def setUpClass(cls):
        """Set up shared test data."""
        super().setUpClass()
        cls.MailMail = cls.env["mail.mail"]
        cls.ICP = cls.env["ir.config_parameter"].sudo()
        # set the delayed deletion days parameter
        cls.ICP.set_param("mail_delayed_deletion.days", "7")

    def _create_mail(self, auto_delete=True, subject="Test mail"):
        """Helper to create a mail.mail record."""
        return self.MailMail.create(
            {
                "subject": subject,
                "body_html": "<p>Test body</p>",
                "email_from": "test@example.com",
                "email_to": "dest@example.com",
                "auto_delete": auto_delete,
            }
        )

    def test_01_delayed_deletion_field_exists(self):
        """Check that the delayed_deletion field is present on mail.mail."""
        mail = self._create_mail()
        self.assertFalse(mail.delayed_deletion)

    def test_02_get_delayed_deletion_days(self):
        """Check that _get_delayed_deletion_days returns the configured value."""
        self.ICP.set_param("mail_delayed_deletion.days", "5")
        mail = self._create_mail()
        days = mail._get_delayed_deletion_days()
        self.assertEqual(days, 5)

    def test_03_delay_auto_delete_sets_date(self):
        """Check that _delay_auto_delete disables auto_delete and sets a date."""
        self.ICP.set_param("mail_delayed_deletion.days", "7")
        mail = self._create_mail(auto_delete=True)
        self.assertTrue(mail.auto_delete)
        self.assertFalse(mail.delayed_deletion)
        mail._delay_auto_delete()
        self.assertFalse(mail.auto_delete)
        self.assertTrue(mail.delayed_deletion)
        # the scheduled date must be approximately 7 days from now
        expected = datetime.today() + timedelta(days=7)
        delta = abs((mail.delayed_deletion - expected).total_seconds())
        self.assertLess(delta, 60)

    def test_04_delay_auto_delete_skips_when_no_days(self):
        """Check that _delay_auto_delete does nothing when days is 0."""
        self.ICP.set_param("mail_delayed_deletion.days", "0")
        mail = self._create_mail(auto_delete=True)
        self.assertTrue(mail.auto_delete)
        mail._delay_auto_delete()
        # auto_delete must remain unchanged when days is 0
        self.assertTrue(mail.auto_delete)
        self.assertFalse(mail.delayed_deletion)

    def test_05_delay_auto_delete_skips_non_auto_delete(self):
        """Check that _delay_auto_delete ignores mails without auto_delete."""
        self.ICP.set_param("mail_delayed_deletion.days", "7")
        mail = self._create_mail(auto_delete=False)
        self.assertFalse(mail.auto_delete)
        mail._delay_auto_delete()
        self.assertFalse(mail.auto_delete)
        self.assertFalse(mail.delayed_deletion)

    def test_06_postprocess_sets_delayed_deletion(self):
        """Check that _postprocess_sent_message triggers delayed deletion."""
        self.ICP.set_param("mail_delayed_deletion.days", "7")
        mail = self._create_mail(auto_delete=True)
        self.assertTrue(mail.auto_delete)
        # call _postprocess_sent_message with no failure (successful send)
        mail._postprocess_sent_message(
            success_pids=self.env["res.partner"],
            failure_reason=False,
            failure_type=None,
        )
        # auto_delete must have been turned off and a date set
        self.assertFalse(mail.auto_delete)
        self.assertTrue(mail.delayed_deletion)

    def test_07_postprocess_skips_on_failure(self):
        """Check that _postprocess_sent_message skips delay on non-recipient failure."""
        self.ICP.set_param("mail_delayed_deletion.days", "7")
        mail = self._create_mail(auto_delete=True)
        # call with a non-RECIPIENT failure type — delay must NOT be applied
        mail._postprocess_sent_message(
            success_pids=self.env["res.partner"],
            failure_reason="SMTP error",
            failure_type="mail_smtp",
        )
        # auto_delete must stay True and no date set
        self.assertTrue(mail.auto_delete)
        self.assertFalse(mail.delayed_deletion)

    def test_08_postprocess_immediate_deletion_context(self):
        """Check that mail_immediate_deletion=True bypasses delay and deletes mail."""
        self.ICP.set_param("mail_delayed_deletion.days", "7")
        mail = self._create_mail(auto_delete=True)
        mail_id = mail.id
        # with mail_immediate_deletion context, delay is bypassed so auto_delete
        # stays True and the base implementation deletes the mail immediately
        mail.with_context(mail_immediate_deletion=True)._postprocess_sent_message(
            success_pids=self.env["res.partner"],
            failure_reason=False,
            failure_type=None,
        )
        # the mail must have been immediately deleted (no delayed_deletion set)
        self.assertFalse(self.MailMail.browse(mail_id).exists())

    def test_09_action_delayed_deletion_unlinking(self):
        """Check that action_delayed_deletion removes mails past their date."""
        self.ICP.set_param("mail_delayed_deletion.days", "7")
        mail_past = self._create_mail(subject="Past mail")
        mail_future = self._create_mail(subject="Future mail")
        # manually set deletion dates to simulate past and future deadlines
        yesterday = datetime.today() - timedelta(days=1)
        next_week = datetime.today() + timedelta(days=7)
        mail_past.write({"auto_delete": False, "delayed_deletion": yesterday})
        mail_future.write({"auto_delete": False, "delayed_deletion": next_week})
        self.MailMail.action_delayed_deletion()
        # mail_past must have been deleted
        self.assertFalse(mail_past.exists())
        # mail_future must still exist
        self.assertTrue(mail_future.exists())

    def test_10_form_view_fields(self):
        """Check that delayed_deletion field is present in the module's view arch."""
        from lxml import etree

        # inspect the inherited view arch directly to verify the field was added
        view = self.env.ref("mail_delayed_deletion.email_message_tree_view")
        arch = etree.fromstring(view.arch)
        field_names = [el.get("name") for el in arch.iter("field")]
        self.assertIn("delayed_deletion", field_names)
