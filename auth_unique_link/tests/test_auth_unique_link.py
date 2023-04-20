# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Apr 2023

from datetime import datetime, timedelta

from odoo import SUPERUSER_ID, api, fields
from odoo.tests import common
from odoo.exceptions import AccessDenied


class TestAuthUniqueLink(common.TransactionCase):
    """ """

    def setUp(self):
        super().setUp()
        self.public_user = self.env.ref("base.public_user")

    def _in_portal(self, user_id):
        return self.env.ref("base.group_portal") in user_id.groups_id

    def _give_portal_access(self, partner_id):
        PortalWizard = self.env["portal.wizard"]
        PortalWizardUser = self.env["portal.wizard.user"]
        wizard_id = PortalWizard.sudo().create({})
        wizard_user_id = PortalWizardUser.sudo().create(
            {
                "wizard_id": wizard_id.id,
                "partner_id": partner_id.id,
                "email": partner_id.email,
                "in_portal": True,
            }
        )
        return wizard_id.action_apply()

    def _get_user_with_portal_access(self):
        # get a demo partner
        partner_id = self.env.ref("base.res_partner_4")
        # give portal access if necessary
        user_id = partner_id.user_ids and partner_id.user_ids[0] or False
        if not user_id or not self._in_portal(user_id):
            self._give_portal_access(partner_id)
            user_id = partner_id.user_ids and partner_id.user_ids[0] or False
        # ensure portal access is active
        self.assertTrue(self._in_portal(user_id))
        return user_id

    def _get_impersonate_wizard(self, user_id):
        # use our wizard to generate an access token
        PartnerImpersonateWizard = self.env["res.partner.impersonate"]
        wizard_id = PartnerImpersonateWizard.sudo().create({"user_id": user_id.id})
        # check that the token is not set (it should in the web view)
        self.assertFalse(wizard_id.token)
        wizard_id.action_generate_new_signin_link()
        # invalidate cache to force related field update
        wizard_id.invalidate_cache()
        # ensure a token is properly generated
        self.assertNotIsInstance(wizard_id.token, bool)
        self.assertIsInstance(wizard_id.token, str)
        # ensure that both token are the same (linked as related)
        self.assertEqual(wizard_id.token, user_id.signin_link_token)
        return wizard_id

    def test_01_res_partner_impersonate(self):
        """ """
        # generate user_id and wizard_id
        user_id = self._get_user_with_portal_access()
        wizard_id = self._get_impersonate_wizard(user_id)

        # check that an already logged user is not able to check credentials
        with self.assertRaises(AccessDenied):
            self.env["res.users"].sudo()._check_credentials(
                wizard_id.token, {"interactive": True}
            )
        # check the concerned already logged user is able to check credentials
        self.env["res.users"].with_user(user_id)._check_credentials(
            wizard_id.token, {"interactive": True}
        )
        # check anonymous user is able to check credentials
        self.env["res.users"].with_user(user_id)._check_credentials(
            wizard_id.token, {"interactive": True}
        )

    def test_02_signin_link_expiration(self):
        MINUTES = 20
        ICP = self.env["ir.config_parameter"].sudo()
        ICP.set_param("auth_unique_link.expiration_minutes", MINUTES)

        exp_limit_low = datetime.now() + timedelta(minutes=+MINUTES)
        # generate user_id and wizard_id
        user_id = self._get_user_with_portal_access()
        wizard_id = self._get_impersonate_wizard(user_id)
        exp_limit_high = datetime.now() + timedelta(minutes=+MINUTES)

        self.assertGreaterEqual(user_id.signin_link_expiration, exp_limit_low)
        self.assertLessEqual(user_id.signin_link_expiration, exp_limit_high)
