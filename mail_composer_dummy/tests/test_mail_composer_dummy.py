# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Mar 2026

import logging

from odoo.tests.common import TransactionCase


class TestMailComposerDummy(TransactionCase):
    """Tests for mail_composer_dummy module."""

    @classmethod
    def setUpClass(cls):
        """Set up shared test data."""
        super().setUpClass()
        cls.MailComposer = cls.env["mail.compose.message"]

    def _make_composer(self, email_to=False, email_cc=False, **kwargs):
        """Create a mass-mail composer with optional custom recipients."""
        vals = {
            "composition_mode": "mass_mail",
            "subject": "Test Subject",
            "body": "<p>Test body</p>",
        }
        if email_to:
            vals["email_to"] = email_to
        if email_cc:
            vals["email_cc"] = email_cc
        vals.update(kwargs)
        return self.MailComposer.create(vals)

    def test_01_email_to_injected(self):
        """email_to is injected into mail values when the field is set."""
        composer = self._make_composer(email_to="custom@example.com")
        mail_values = composer._prepare_mail_values([0])
        self.assertEqual(mail_values[0]["email_to"], "custom@example.com")

    def test_02_email_cc_injected(self):
        """email_cc is injected into mail values when the field is set."""
        composer = self._make_composer(email_cc="cc@example.com")
        mail_values = composer._prepare_mail_values([0])
        self.assertEqual(mail_values[0]["email_cc"], "cc@example.com")

    def test_03_both_recipients_injected(self):
        """both email_to and email_cc are injected when both fields are set."""
        composer = self._make_composer(
            email_to="to@example.com",
            email_cc="cc@example.com",
        )
        mail_values = composer._prepare_mail_values([0])
        self.assertEqual(mail_values[0]["email_to"], "to@example.com")
        self.assertEqual(mail_values[0]["email_cc"], "cc@example.com")

    def test_04_no_injection_when_fields_empty(self):
        """email_to and email_cc are absent from mail values when fields are not set."""
        composer = self._make_composer()
        mail_values = composer._prepare_mail_values([0])
        # base static values should not include email_to / email_cc
        self.assertNotIn("email_to", mail_values[0])
        self.assertNotIn("email_cc", mail_values[0])

    def test_05_email_to_wins_when_already_in_mail_values(self):
        """our email_to wins even when the base already has an email_to value."""
        # res.partner without a template: _message_get_default_recipients
        # populates email_to. our value must override it.
        partner = self.env["res.partner"].search([("email", "!=", False)], limit=1)
        composer = self._make_composer(
            email_to="winner@example.com",
            model="res.partner",
        )
        mail_values = composer._prepare_mail_values([partner.id])
        self.assertEqual(mail_values[partner.id]["email_to"], "winner@example.com")

    def test_06_multiple_res_ids_and_override_logged(self):
        """injection applies to every res_id and emits an override log per record."""
        partners = self.env["res.partner"].search([], limit=3)
        res_ids = partners.ids
        composer = self._make_composer(
            email_to="multi@example.com",
            email_cc="multi-cc@example.com",
            model="res.partner",
        )
        with self.assertLogs(
            "odoo.addons.mail_composer_dummy", level=logging.INFO
        ) as log_cm:
            mail_values = composer._prepare_mail_values(res_ids)
        for res_id in res_ids:
            self.assertEqual(mail_values[res_id]["email_to"], "multi@example.com")
            self.assertEqual(mail_values[res_id]["email_cc"], "multi-cc@example.com")
        # one "Overriding" log line per field per record
        self.assertTrue(any("Overriding 'email_to'" in msg for msg in log_cm.output))
        self.assertTrue(any("Overriding 'email_cc'" in msg for msg in log_cm.output))
