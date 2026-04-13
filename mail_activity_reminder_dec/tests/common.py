# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Apr 2026

from datetime import date

from odoo.tests.common import TransactionCase


class TestMailActivityReminderDecCommon(TransactionCase):
    """Common base class for mail_activity_reminder_dec tests."""

    @classmethod
    def setUpClass(cls):
        """Set up shared test data."""
        super().setUpClass()
        cls.ActivityType = cls.env["mail.activity.type"]
        cls.Activity = cls.env["mail.activity"]
        cls.User = cls.env["res.users"]
        cls.Partner = cls.env["res.partner"]
        cls.activity_type = cls.env.ref("mail.mail_activity_data_todo")
        cls.test_user = cls.env.ref("base.user_demo")
        cls.test_partner = cls.env.ref("base.partner_demo")
        cls.activity = cls.Activity.create(
            {
                "activity_type_id": cls.activity_type.id,
                "res_model_id": cls.env["ir.model"]._get("res.partner").id,
                "res_id": cls.test_partner.id,
                "user_id": cls.test_user.id,
                "date_deadline": date.today(),
                "summary": "Test activity",
            }
        )
