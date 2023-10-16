# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Oct 2023

from odoo.tests.common import tagged
from odoo.addons.auth_signup_delegate.tests.common import (
    TestAuthSignupDelegateControllerBase,
)


@tagged("-at_install", "post_install")
class TestAuthSignupDelegateFencing(TestAuthSignupDelegateControllerBase):
    def setUp(self):
        super().setUp()

    def test_01_new_contact(self):
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
        new_contact_id = self.partner.child_ids[0]
        # check that the new contact cannot access its parent data
        self.assertFalse(new_contact_id.inherit_commercial_partner)
        self.assertEqual(new_contact_id.commercial_partner_id, new_contact_id)
        self.assertEqual(new_contact_id.unfenced_commercial_partner_id, self.partner)
