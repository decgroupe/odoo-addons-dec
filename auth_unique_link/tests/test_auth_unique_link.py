# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Apr 2023

from datetime import datetime, timedelta

from odoo.exceptions import AccessDenied
from .common import TestAuthUniqueLinkCommon



class TestAuthUniqueLink(TestAuthUniqueLinkCommon):
    """ """

    def test_01_res_partner_impersonate(self):
        """ """
        # generate user_id and wizard_id
        user_id = self._get_user_with_portal_access("base.res_partner_4")
        wizard_id = self._get_impersonate_wizard(user_id)

        # check that an already logged user is not able to check credentials
        with self.assertRaises(AccessDenied), self.cr.savepoint():
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
        user_id = self._get_user_with_portal_access("base.res_partner_4")
        wizard_id = self._get_impersonate_wizard(user_id)
        exp_limit_high = datetime.now() + timedelta(minutes=+MINUTES)

        self.assertGreaterEqual(user_id.signin_link_expiration, exp_limit_low)
        self.assertLessEqual(user_id.signin_link_expiration, exp_limit_high)
