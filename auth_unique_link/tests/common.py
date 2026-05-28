# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Mar 2024

import random
from contextlib import contextmanager
from unittest.mock import patch

from odoo import Command
from odoo.tests import common


class TestAuthUniqueLinkCommon(common.TransactionCase):
    """ """

    def setUp(self):
        super().setUp()
        self.public_user = self.env.ref("base.public_user")

    def _in_portal(self, user_id):
        return user_id._is_portal()

    def _give_portal_access(self, partner_id):
        PortalWizard = self.env["portal.wizard"]
        # unset active_id/active_ids otherwise wizard.user_ids will be filled with
        # garbage (because not check for `active_model` in `_default_user_ids`)
        wizard_id = (
            PortalWizard.with_context(active_id=False, active_ids=False)
            .sudo()
            .create({"partner_ids": [Command.set(partner_id.ids)]})
        )
        for wizard_user_id in wizard_id.user_ids:
            if not wizard_user_id.is_portal:
                wizard_user_id.action_grant_access()
        return None

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

    def _prepare_basic_token(self, user_id):
        """Prepare a fresh basic (6-digit) token for user_id and return
        a (actual_token, wrong_token) tuple where wrong_token is a
        different 6-digit code guaranteed not to match.

        The token is written on the test cursor directly so that both the
        test cursor and any env created from it (via _patch_registry_cursor)
        can read the committed-in-savepoint value.
        """
        actual = str(random.SystemRandom().randint(0, 999_999)).zfill(6)
        user_id.sudo().write(
            {
                "signin_link_token": actual,
                "signin_link_expiration": False,
                "signin_link_token_failures": 0,
            }
        )
        # shift by 1 mod 10^6 to get a code that is never equal to actual
        wrong = str((int(actual) + 1) % 1_000_000).zfill(6)
        return actual, wrong

    @contextmanager
    def _patch_registry_cursor(self):
        """Patch registry.cursor() to yield the test cursor (no commit or
        close) so that writes inside _check_credentials remain visible to the
        test transaction.

        This is needed because in production _check_credentials opens a new
        cursor to persist the failure counter even after the auth cursor is
        rolled back on AccessDenied.  In tests, the portal user row lives in
        an uncommitted savepoint; new cursors cannot see it, so we redirect
        the registry cursor to the test cursor instead.
        """
        test_cr = self.env.cr

        @contextmanager
        def _fake_cursor():
            # yield the test cursor; skip commit/close to preserve test isolation
            yield test_cr

        with patch.object(self.env.registry, "cursor", _fake_cursor):
            yield

    def _get_impersonate_wizard(self, user_id):
        # use our wizard to generate an access token
        PartnerImpersonateWizard = self.env["res.partner.impersonate"]
        wizard_id = PartnerImpersonateWizard.sudo().create({"user_id": user_id.id})
        # check that the token is not set (it should in the web view)
        self.assertFalse(wizard_id.token)
        wizard_id.action_generate_new_signin_link()
        # invalidate cache to force related field update
        wizard_id.invalidate_recordset()
        # ensure a token is properly generated
        self.assertNotIsInstance(wizard_id.token, bool)
        self.assertIsInstance(wizard_id.token, str)
        # ensure that both token are the same (linked as related)
        self.assertEqual(wizard_id.token, user_id.signin_link_token)
        return wizard_id
