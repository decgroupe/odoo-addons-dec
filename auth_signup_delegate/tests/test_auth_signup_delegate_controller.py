# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Oct 2023

from odoo.tests.common import tagged
from odoo.addons.auth_signup_delegate.tests.common import (
    TestAuthSignupDelegateControllerBase,
)


@tagged("-at_install", "post_install")
class TestAuthSignupDelegateController(TestAuthSignupDelegateControllerBase):
    def setUp(self):
        super().setUp()

    def test_01_get_delegate_page(self):
        self._prepare_partner_delegation()
        # test GET
        res = self.url_open(self._get_delegate_url())
        self.assertEqual(res.status_code, 200)

    def test_02_new_contact_without_valid_delegation_token(self):
        # test POST
        payload = {
            **self._get_contact_vals(),
            "csrf_token": self._get_crsf_token(),
        }
        # try without token
        res = self.url_open(self._get_delegate_url(), data=payload)
        self.assertEqual(res.status_code, 200)
        self.assertIn("Invalid Token", res.text)
        # try with a fake token
        payload["token"] = "123456789"
        res = self.url_open(self._get_delegate_url(), data=payload)
        self.assertEqual(res.status_code, 200)
        self.assertIn("Invalid Token", res.text)

    def test_03_new_contact_without_portal_access(self):
        # generate a token but don't give portal access
        self._prepare_partner_delegation()
        # test POST
        payload = {
            **self._get_contact_vals(),
            "csrf_token": self._get_crsf_token(),
        }
        res = self.url_open(self._get_delegate_url(), data=payload, timeout=3600)
        self.assertEqual(res.status_code, 200)
        self.assertIn("Your portal access must be active", res.text)

    def test_04_new_contact_without_active_portal_access(self):
        # generate a token and give portal access
        self._prepare_partner_delegation(give_portal_access=True)
        # test POST
        payload = {
            **self._get_contact_vals(),
            "csrf_token": self._get_crsf_token(),
        }
        res = self.url_open(self._get_delegate_url(), data=payload, timeout=3600)
        self.assertEqual(res.status_code, 200)
        self.assertIn("Your portal access must be active", res.text)

    def test_05_new_contact(self):
        # give portal access, because the token owner must have a user_id
        self._prepare_partner_delegation(give_portal_access=True, signup_complete=True)
        # test POST
        payload = {
            **self._get_contact_vals(),
            "csrf_token": self._get_crsf_token(),
        }
        res = self.url_open(self._get_delegate_url(), data=payload, timeout=3600)
        self.assertEqual(res.status_code, 200)
        self.assertRegex(
            res.text,
            "Contact.*has been created and a confirmation e-mail has been sent",
        )
        # invalidate cache because http have its own cursor
        self.partner.invalidate_cache()
        self.assertEqual(len(self.partner.child_ids), 1)

    def test_06_new_contact_that_already_exist(self):
        # create an orphelin contact
        janitor_partner = self.env["res.partner"].create(self._get_contact_vals())
        janitor_partner.give_portal_access()
        janitor_partner.signup_cancel()
        # give portal access to our main partner
        self._prepare_partner_delegation(give_portal_access=True, signup_complete=True)
        # test POST
        payload = {
            **self._get_contact_vals(),
            "csrf_token": self._get_crsf_token(),
        }
        res = self.url_open(self._get_delegate_url(), data=payload, timeout=3600)
        self.assertEqual(res.status_code, 200)
        self.assertIn(
            "This email already exists for a contact that is not a member "
            "of your company. You cannot grant him a portal access",
            res.text,
        )
        # give our orphelin a parent and retry
        janitor_partner.parent_id = self.partner
        # re-test POST
        res = self.url_open(self._get_delegate_url(), data=payload, timeout=3600)
        self.assertEqual(res.status_code, 200)
        self.assertRegex(res.text, "Contact.*already have an access to the Portal")
