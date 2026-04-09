# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Apr 2026

from odoo.tests.common import TransactionCase


class MailChannelUserGroupCommon(TransactionCase):
    """Common setup for mail_channel_user_group tests."""

    @classmethod
    def setUpClass(cls):
        """Set up shared test data."""
        super().setUpClass()
        cls.user_internal = cls.env.ref("base.user_demo")
        cls.partner_internal = cls.user_internal.partner_id
        cls.channel = cls.env["discuss.channel"].channel_create(
            name="Test Channel", group_id=None
        )
        cls.channel.sudo().add_members([cls.partner_internal.id])
