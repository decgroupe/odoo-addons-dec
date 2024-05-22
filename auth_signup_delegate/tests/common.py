# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Oct 2023

from odoo import http
from odoo.tests.common import HttpCase


class TestAuthSignupDelegateControllerBase(HttpCase):
    def setUp(self):
        super().setUp()
        self.partner = self.env["res.partner"].create(
            {"name": "New Partner", "is_company": True}
        )

    def _prepare_partner_delegation(
        self, give_portal_access=False, signup_complete=False
    ):
        # generate a new delegation token
        self.partner.delegate_signup_prepare()
        # give portal access, because the token owner must have a user_id
        if give_portal_access:
            self.partner.email = "partner@domain.com"
            self.partner.give_portal_access()
            user_id = self.partner.user_ids
            if signup_complete:
                # invalidate signup token
                self.partner.signup_cancel()
                # most important, set a login date to update user's state from
                # new to active (note that this function is tagged api.model)
                self.env["res.users"].with_user(user_id)._update_last_login()
                self.assertEqual(user_id.state, "active")

    def _get_crsf_token(self):
        # Get csrf_token
        self.authenticate(None, None)
        csrf_token = http.WebRequest.csrf_token(self)
        return csrf_token

    def _get_delegate_url(self):
        return "/signup/delegate/%s" % (self.partner.delegate_signup_token)

    def _get_contact_vals(self):
        return {
            "name": "Contact 1",
            "email": "janitor@domain.com",
            "function": "Janitor",
        }
