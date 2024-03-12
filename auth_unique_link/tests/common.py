# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Mar 2024


from odoo.tests import common


class TestAuthUniqueLinkCommon(common.TransactionCase):
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

    def _get_user_with_portal_access(self, partner_xml_id):
        # get a demo partner
        partner_id = self.env.ref(partner_xml_id)
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