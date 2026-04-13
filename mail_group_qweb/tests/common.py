# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Apr 2026

import logging
from contextlib import contextmanager
from unittest.mock import patch

from odoo.tests import new_test_user
from odoo.tests.common import TransactionCase

_test_logger = logging.getLogger("odoo.tests")


class TestMailGroupQwebCommon(TransactionCase):
    """Common fixtures and helpers for mail_group_qweb tests."""

    @classmethod
    def setUpClass(cls):
        """Set up shared test data for mail_group_qweb tests."""
        super().setUpClass()
        cls.Mail = cls.env["mail.mail"]
        # create an internal user with an email address
        cls.user_internal = new_test_user(
            cls.env,
            login="internal_user@test.com",
            groups="base.group_user",
            name="Internal User",
            email="internal_user@test.com",
        )
        # create a portal user with an email address
        cls.user_portal = new_test_user(
            cls.env,
            login="portal_user@test.com",
            groups="base.group_portal",
            name="Portal User",
            email="portal_user@test.com",
        )
        # create a test mail group with public access and an alias
        cls.test_group = cls.env["mail.group"].create(
            {
                "name": "Test Mail Group",
                "access_mode": "public",
                "alias_name": "test-mail-group",
            }
        )
        # add 3 members: email-only (customer), internal user, portal user
        cls.member_customer = cls.env["mail.group.member"].create(
            {
                "mail_group_id": cls.test_group.id,
                "email": "customer@external.com",
            }
        )
        cls.member_internal = cls.env["mail.group.member"].create(
            {
                "mail_group_id": cls.test_group.id,
                "partner_id": cls.user_internal.partner_id.id,
            }
        )
        cls.member_portal = cls.env["mail.group.member"].create(
            {
                "mail_group_id": cls.test_group.id,
                "partner_id": cls.user_portal.partner_id.id,
            }
        )
        # create a message from an outsider (not a group member) so all members
        # receive it
        cls.test_message = cls.env["mail.group.message"].create(
            {
                "subject": "Hello World",
                "mail_group_id": cls.test_group.id,
                "email_from": '"Outsider" <outsider@example.com>',
                "body": "<p>Test message body.</p>",
            }
        )

    @contextmanager
    def patch_mail_unlink(self):
        """Disable mail.mail.unlink so sent mails are kept for inspection."""

        def _disabled_unlink(self):
            _test_logger.warning("Unlink disabled for `mail.mail`")

        with patch.object(type(self.Mail), "unlink", _disabled_unlink):
            yield
