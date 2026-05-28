# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Apr 2023

import logging
from datetime import datetime, timedelta

from odoo.exceptions import AccessDenied

from .common import TestAuthUniqueLinkCommon

_logger = logging.getLogger(__name__)


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
                {"type": "password", "password": wizard_id.token},
                {"interactive": True},
            )
        # check the concerned already logged user is able to check credentials
        self.env["res.users"].with_user(user_id)._check_credentials(
            {"type": "password", "password": wizard_id.token},
            {"interactive": True},
        )
        # check anonymous user is able to check credentials
        self.env["res.users"].with_user(user_id)._check_credentials(
            {"type": "password", "password": wizard_id.token},
            {"interactive": True},
        )

    def test_02_signin_link_expiration(self):
        MINUTES = 20
        ICP = self.env["ir.config_parameter"].sudo()
        ICP.set_param("auth_unique_link.expiration_minutes", MINUTES)

        exp_limit_low = datetime.now() + timedelta(minutes=+MINUTES)
        # generate user_id and wizard_id
        user_id = self._get_user_with_portal_access("base.res_partner_4")
        _wizard_id = self._get_impersonate_wizard(user_id)
        exp_limit_high = datetime.now() + timedelta(minutes=+MINUTES)

        self.assertGreaterEqual(user_id.signin_link_expiration, exp_limit_low)
        self.assertLessEqual(user_id.signin_link_expiration, exp_limit_high)

    def test_03_basic_token_failure_counter_increments(self):
        """Submit wrong 6-digit codes and verify the failure counter grows."""
        user_id = self._get_user_with_portal_access("base.res_partner_4")
        _actual, wrong = self._prepare_basic_token(user_id)
        # first wrong attempt: counter must reach 1
        # Note: avoid assertRaises here because its _FlushingSavepoint would
        # roll back the ORM write done in the dedicated cursor.
        with self._patch_registry_cursor():
            try:
                self.env["res.users"].with_user(user_id)._check_credentials(
                    {"type": "password", "password": wrong},
                    {"interactive": True},
                )
                self.fail("Expected AccessDenied")
            except AccessDenied:
                _logger.debug("Expected AccessDenied caught", exc_info=True)
        user_id.invalidate_recordset()
        self.assertEqual(user_id.sudo().signin_link_token_failures, 1)
        # second wrong attempt: counter must reach 2
        with self._patch_registry_cursor():
            try:
                self.env["res.users"].with_user(user_id)._check_credentials(
                    {"type": "password", "password": wrong},
                    {"interactive": True},
                )
                self.fail("Expected AccessDenied")
            except AccessDenied:
                _logger.debug("Expected AccessDenied caught", exc_info=True)
        user_id.invalidate_recordset()
        self.assertEqual(user_id.sudo().signin_link_token_failures, 2)

    def test_04_basic_token_cleared_after_three_failures(self):
        """Token must be cleared and counter reset after 3 consecutive bad
        attempts with a wrong 6-digit code.
        """
        user_id = self._get_user_with_portal_access("base.res_partner_2")
        _actual, wrong = self._prepare_basic_token(user_id)
        self.assertTrue(user_id.sudo().signin_link_token)
        # three wrong attempts — avoid assertRaises (see test_03)
        for _i in range(3):
            with self._patch_registry_cursor():
                try:
                    self.env["res.users"].with_user(user_id)._check_credentials(
                        {"type": "password", "password": wrong},
                        {"interactive": True},
                    )
                    self.fail("Expected AccessDenied")
                except AccessDenied:
                    _logger.debug("Expected AccessDenied caught", exc_info=True)
        user_id.invalidate_recordset()
        # token must be gone and counter back to 0
        self.assertFalse(user_id.sudo().signin_link_token)
        self.assertEqual(user_id.sudo().signin_link_token_failures, 0)

    def test_05_basic_token_counter_reset_on_new_token(self):
        """Calling signin_link_prepare resets the failure counter to 0."""
        user_id = self._get_user_with_portal_access("base.res_partner_4")
        _actual, wrong = self._prepare_basic_token(user_id)
        # produce one failure — avoid assertRaises (see test_03)
        with self._patch_registry_cursor():
            try:
                self.env["res.users"].with_user(user_id)._check_credentials(
                    {"type": "password", "password": wrong},
                    {"interactive": True},
                )
                self.fail("Expected AccessDenied")
            except AccessDenied:
                _logger.debug("Expected AccessDenied caught", exc_info=True)
        user_id.invalidate_recordset()
        self.assertEqual(user_id.sudo().signin_link_token_failures, 1)
        # requesting a new token must reset the counter; pass an expiration so
        # that signin_link_prepare actually regenerates the token even though the
        # existing one is still valid (no-expiry token would be kept as-is)
        user_id.signin_link_prepare(
            expiration=datetime.now() + timedelta(minutes=10), basic=True
        )
        user_id.invalidate_recordset()
        self.assertEqual(user_id.sudo().signin_link_token_failures, 0)

    def test_06_long_token_wrong_password_no_counter(self):
        """A wrong submission that is not a 6-digit code must not increment
        the failure counter, even when the stored token is a 6-digit code.
        """
        user_id = self._get_user_with_portal_access("base.res_partner_4")
        _actual, _wrong = self._prepare_basic_token(user_id)
        # submit a wrong password that is NOT a 6-digit code
        with self.assertRaises(AccessDenied):
            self.env["res.users"].with_user(user_id)._check_credentials(
                {"type": "password", "password": "wrongpassword"},
                {"interactive": True},
            )
        user_id.invalidate_recordset()
        # counter must remain at 0
        self.assertEqual(user_id.sudo().signin_link_token_failures, 0)
