# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Oct 2023

from odoo.exceptions import UserError
from odoo.tests.common import Form, TransactionCase


class TestAuthSignupDelegate(TransactionCase):
    def setUp(self):
        super().setUp()
        self.partner = self.env["res.partner"].create(
            {
                "name": "New Partner",
                "is_company": True,
            }
        )

    def _in_portal(self, partner_id):
        res = False
        if partner_id.user_ids:
            res = self.env.ref("base.group_portal") in partner_id.user_ids[0].groups_id
        return res

    def _create_wizard(self, partner_id):
        partner_id.ensure_one()
        wizard_id = (
            self.env["res.partner.signup.delegate"]
            .with_context(active_id=partner_id.id, active_model=partner_id._name)
            .create({})
        )
        return wizard_id

    def test_01_give_portal_access(self):
        self.assertFalse(self._in_portal(self.partner))
        with self.assertRaisesRegex(
            UserError, "Some contacts don't have a valid email"
        ):
            self.partner.give_portal_access()
        self.partner.email = "partner@domain.com"
        self.partner.give_portal_access()
        self.assertTrue(self._in_portal(self.partner))

    def test_02_wizard_actions_without_partner(self):
        wizard_form = Form(self.env["res.partner.signup.delegate"])
        wizard_id = wizard_form.save()
        with self.assertRaisesRegex(ValueError, "Expected singleton"):
            wizard_id.action_init_signup_delegation()
        # Cancelling delegation do nothing on empty records
        wizard_id.action_cancel_signup_delegation()

    def test_03_delegation_token_management(self):
        self.assertFalse(self.partner.delegate_signup_token)
        self.assertFalse(self._in_portal(self.partner))
        # generate a new token
        self.partner.delegate_signup_prepare()
        # check token is set
        self.assertTrue(self.partner.delegate_signup_token)
        # keep current token in memory
        token = self.partner.delegate_signup_token
        # generate a new token
        self.partner.delegate_signup_prepare()
        # check token is always set
        self.assertTrue(self.partner.delegate_signup_token)
        # check token is still the same
        self.assertEqual(self.partner.delegate_signup_token, token)

    def test_04_delegate_without_initial_portal_access(self):
        self.assertFalse(self.partner.delegate_signup_token)
        self.assertFalse(self._in_portal(self.partner))
        wizard_id = self._create_wizard(self.partner)
        with self.assertRaisesRegex(ValueError, "Expected singleton"):
            wizard_id.action_init_signup_delegation()
        self.partner.email = "partner@domain.com"
        self.partner.give_portal_access()
        wizard_id = self._create_wizard(self.partner)
        wizard_id.action_init_signup_delegation()
        # check token is set
        self.assertTrue(self.partner.delegate_signup_token)
        # disable delegation
        wizard_id.action_cancel_signup_delegation()
        # check token is clear
        self.assertFalse(self.partner.delegate_signup_token)

    # def test_05(self):
    #     wizard_form = Form(self.env["res.partner.signup.delegate"])

    # def test_tour(self):
    #     delegate_url = "/signup/delegate/%s" % (token)
    #     payload = {}
    #     res = self.url_open(delegate_url, data=payload)
    #     print(res)
    #     pass
