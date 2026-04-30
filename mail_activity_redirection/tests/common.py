# Copyright 2021 DEC SARL, Inc - All Rights Reserved.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo.tests.common import TransactionCase


class TestMailActivityRedirectionCommon(TransactionCase):
    """Common base class with shared fixtures for mail_activity_redirection tests."""

    @classmethod
    def setUpClass(cls):
        """Set up shared test data."""
        super().setUpClass()
        cls.Redirection = cls.env["mail.activity.redirection"]
        cls.Partner = cls.env["res.partner"]
        cls.ActivityType = cls.env["mail.activity.type"]
        cls.IrModel = cls.env["ir.model"]
        # create two regular users for redirection testing
        cls.user_original = cls.env["res.users"].create(
            {
                "name": "Original User",
                "login": "test_original_user@example.com",
                "email": "test_original_user@example.com",
                "groups_id": cls.env.ref("base.group_user").ids,
            }
        )
        cls.user_target = cls.env["res.users"].create(
            {
                "name": "Target User",
                "login": "test_target_user@example.com",
                "email": "test_target_user@example.com",
                "groups_id": cls.env.ref("base.group_user").ids,
            }
        )
        # create a partner used as the mixin record for activity scheduling
        cls.partner = cls.Partner.create({"name": "Test Partner"})
        # resolve activity type for use in tests
        cls.activity_type = cls.env.ref("mail.mail_activity_data_todo")
        cls.partner_model = cls.IrModel._get("res.partner")
