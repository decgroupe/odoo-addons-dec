# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Apr 2026

from odoo.tests.common import TransactionCase


class TestMailDisableAutoSubscribeCommon(TransactionCase):
    """Common base class with shared fixtures for mail_disable_auto_subscribe tests."""

    @classmethod
    def setUpClass(cls):
        """Set up shared test data."""
        super().setUpClass()
        # create a partner that allows all auto-subscribe behaviours
        cls.partner_all = cls.env["res.partner"].create(
            {
                "name": "Partner All Subscribe",
                "auto_subscribe_on_tag": True,
                "auto_subscribe_on_message": True,
                "auto_subscribe_on_activity": True,
            }
        )
        # create a partner that refuses all auto-subscribe behaviours
        cls.partner_none = cls.env["res.partner"].create(
            {
                "name": "Partner No Subscribe",
                "auto_subscribe_on_tag": False,
                "auto_subscribe_on_message": False,
                "auto_subscribe_on_activity": False,
            }
        )
        # create an active internal user that allows all auto-subscribe behaviours
        cls.user_all = cls.env["res.users"].create(
            {
                "name": "User All Subscribe",
                "login": "user_all_subscribe_test",
                "email": "user_all@example.com",
                "groups_id": [(4, cls.env.ref("base.group_user").id)],
            }
        )
        cls.user_all.partner_id.write(
            {
                "auto_subscribe_on_tag": True,
                "auto_subscribe_on_message": True,
                "auto_subscribe_on_activity": True,
            }
        )
        # create an active internal user that refuses all auto-subscribe behaviours
        cls.user_none = cls.env["res.users"].create(
            {
                "name": "User No Subscribe",
                "login": "user_none_subscribe_test",
                "email": "user_none@example.com",
                "groups_id": [(4, cls.env.ref("base.group_user").id)],
            }
        )
        cls.user_none.partner_id.write(
            {
                "auto_subscribe_on_tag": False,
                "auto_subscribe_on_message": False,
                "auto_subscribe_on_activity": False,
            }
        )
        # a simple model that supports mail.thread — use res.partner itself
        cls.MailMessage = cls.env["mail.message"]
        cls.MailSubtype = cls.env["mail.message.subtype"]
        cls.IrModel = cls.env["ir.model"]
