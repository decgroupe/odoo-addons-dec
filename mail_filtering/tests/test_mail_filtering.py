# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Mar 2026

from unittest.mock import patch

from odoo.tests.common import TransactionCase


class TestMailFiltering(TransactionCase):
    """Tests for mail_filtering module."""

    @classmethod
    def setUpClass(cls):
        """Set up shared test data."""
        super().setUpClass()
        cls.MailServer = cls.env["ir.mail_server"]
        cls.MailMail = cls.env["mail.mail"]
        cls.mail_server = cls.MailServer.create(
            {
                "name": "Test SMTP Server",
                "smtp_host": "localhost",
                "smtp_port": 25,
                "allowed_databases": "*",
            }
        )

    def _create_test_mail(self):
        """Create a minimal outgoing mail for testing."""
        return self.MailMail.create(
            {
                "subject": "Test Subject",
                "body_html": "<p>Test body</p>",
                "email_from": "test@example.com",
                "email_to": "recipient@example.com",
                "state": "outgoing",
                "mail_server_id": self.mail_server.id,
            }
        )

    def test_01_allowed_databases_default_wildcard(self):
        """Verify that allowed_databases defaults to '*' (all databases allowed)."""
        server = self.MailServer.create(
            {
                "name": "Default Server",
                "smtp_host": "localhost",
                "smtp_port": 25,
            }
        )
        self.assertEqual(server.allowed_databases, "*")

    def test_02_send_blocked_when_db_not_in_allowedlist(self):
        """Verify _send returns False when current db is not in allowed_databases."""
        self.mail_server.allowed_databases = "some_other_database,another_db"
        mail = self._create_test_mail()
        result = mail.with_context(raise_if_send_not_allowed=False)._send(
            auto_commit=False,
            raise_exception=False,
            mail_server=self.mail_server,
        )
        self.assertFalse(result)

    def test_03_send_blocked_raises_when_context_flag_set(self):
        """Verify _send raises when raise_if_send_not_allowed=True and db blocked."""
        self.mail_server.allowed_databases = "some_other_database"
        mail = self._create_test_mail()
        with self.assertRaises(Exception) as cm:
            mail.with_context(raise_if_send_not_allowed=True)._send(
                auto_commit=False,
                raise_exception=False,
                mail_server=self.mail_server,
            )
        self.assertIn("not allowed", str(cm.exception))

    def test_04_send_allowed_when_wildcard(self):
        """Verify _send delegates to super when allowed_databases is '*'."""
        self.mail_server.allowed_databases = "*"
        mail = self._create_test_mail()
        super_called = []
        # patch the parent class _send to detect delegation
        base_cls = type(mail).__bases__[0]

        def mock_parent_send(self_inner, *args, **kwargs):
            """Mock that records invocation instead of actually sending."""
            super_called.append(True)
            return True

        with patch.object(base_cls, "_send", mock_parent_send):
            mail._send(
                auto_commit=False,
                raise_exception=False,
                mail_server=self.mail_server,
            )
        self.assertTrue(super_called, "super()._send() was not called when allowed")

    def test_05_send_allowed_when_db_in_allowedlist(self):
        """Verify _send delegates to super when current db is in allowed_databases."""
        dbname = self.env.cr.dbname
        self.mail_server.allowed_databases = dbname
        mail = self._create_test_mail()
        super_called = []
        base_cls = type(mail).__bases__[0]

        def mock_parent_send(self_inner, *args, **kwargs):
            """Mock that records invocation instead of actually sending."""
            super_called.append(True)
            return True

        with patch.object(base_cls, "_send", mock_parent_send):
            mail._send(
                auto_commit=False,
                raise_exception=False,
                mail_server=self.mail_server,
            )
        self.assertTrue(super_called, "super()._send() was not called when allowed")

    def test_06_get_db_process_email_allowedlist_empty(self):
        """Verify _get_db_process_email_allowedlist returns empty list if no config."""
        result = self.MailMail._get_db_process_email_allowedlist()
        self.assertIsInstance(result, list)
