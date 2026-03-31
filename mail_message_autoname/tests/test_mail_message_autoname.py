# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Mar 2026

from odoo import tools
from odoo.tests.common import TransactionCase


class TestMailMessageAutoname(TransactionCase):
    """Tests for mail_message_autoname module."""

    @classmethod
    def setUpClass(cls):
        """Set up shared test data."""
        super().setUpClass()
        cls.partner = cls.env["res.partner"].create({"name": "Test Partner"})
        cls.MailMessage = cls.env["mail.message"]

    def test_01_record_name_set_when_missing(self):
        """record_name is auto-filled when model and res_id are given."""
        msg = self.MailMessage.create(
            {
                "model": "res.partner",
                "res_id": self.partner.id,
                "message_type": "comment",
                "body": "hello",
            }
        )
        self.assertEqual(msg.record_name, self.partner.display_name)

    def test_02_record_name_set_when_explicitly_false(self):
        """record_name is computed even when caller explicitly passes False."""
        msg = self.MailMessage.create(
            {
                "model": "res.partner",
                "res_id": self.partner.id,
                "record_name": False,
                "message_type": "comment",
                "body": "hello",
            }
        )
        self.assertEqual(msg.record_name, self.partner.display_name)

    def test_03_record_name_not_overridden_by_context(self):
        """record_name is left untouched when default_record_name is in context."""
        ctx = {"default_record_name": "My Custom Name"}
        msg = self.MailMessage.with_context(**ctx).create(
            {
                "model": "res.partner",
                "res_id": self.partner.id,
                "record_name": False,
                "message_type": "comment",
                "body": "hello",
            }
        )
        # _autoadd_record_name returns early so record_name stays False/empty
        self.assertFalse(msg.record_name)

    def test_04_record_name_not_set_without_model(self):
        """record_name is not computed when model is missing."""
        msg = self.MailMessage.create(
            {
                "message_type": "comment",
                "body": "hello",
            }
        )
        self.assertFalse(msg.record_name)

    def test_05_record_name_not_overwritten_when_already_set(self):
        """record_name is not overwritten when a non-empty value is already provided."""
        msg = self.MailMessage.create(
            {
                "model": "res.partner",
                "res_id": self.partner.id,
                "record_name": "Custom Name",
                "message_type": "comment",
                "body": "hello",
            }
        )
        self.assertEqual(msg.record_name, "Custom Name")

    def test_06_compute_author_plain_email_reformatted(self):
        """a plain email address with no name part is reformatted to 'email <email>'."""
        plain_email = "yanapa@laposte.net"
        _author_id, email_from = self.partner._message_compute_author(
            author_id=None,
            email_from=plain_email,
            raise_on_email=False,
        )
        # when no partner is found author_id may be falsy
        self.assertFalse(_author_id)
        # the email should have been reformatted to include the address as display name
        expected = tools.formataddr((plain_email, plain_email))
        self.assertEqual(email_from, expected)

    def test_07_compute_author_named_email_unchanged(self):
        """an email with an explicit name part is left as-is."""
        named_email = "John Doe <john@example.com>"
        _author_id, email_from = self.partner._message_compute_author(
            author_id=None,
            email_from=named_email,
            raise_on_email=False,
        )
        # the display name is already present so no reformatting should occur
        self.assertEqual(email_from, named_email)
