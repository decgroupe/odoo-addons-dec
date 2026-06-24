# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Oct 2023

from odoo.tests.common import TransactionCase, new_test_user

from odoo.addons.website.tools import MockRequest


class TestAccountTagTechnical(TransactionCase):
    def setUp(self):
        super().setUp()
        ctx = {
            "mail_create_nolog": True,
            "mail_create_nosubscribe": True,
            "mail_notrack": True,
            "no_reset_password": True,
        }
        self.user = new_test_user(
            self.env,
            login="action_view-user",
            groups="account.group_account_invoice",
            context=ctx,
        )

    def test_01_technical_name(self):
        tag_financing = self.env.ref("account.account_tag_financing")
        tech_name = tag_financing.with_user(self.user).display_name
        self.assertEqual(tech_name, "Financing Activities")
        # enable technical group (not needed since base_user depends on it)
        self.env.ref("base.group_no_one").write({"users": [(4, self.user.id)]})
        self.assertFalse(self.user.has_group("base.group_no_one"))
        # retry with debug mode enabled in mocked http request
        with MockRequest(self.env) as mock:
            # simulate a debug HTTP request so base.group_no_one is active
            mock.session.debug = True
            self.assertTrue(self.user.has_group("base.group_no_one"))
            tech_name = tag_financing.with_user(self.user).display_name
        self.assertEqual(tech_name, "Financing Activities [account_tag_financing]")
