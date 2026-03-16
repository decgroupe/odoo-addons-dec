# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Mar 2026

from unittest.mock import patch

from odoo.modules.registry import Registry
from odoo.sql_db import BaseCursor
from odoo.tests import new_test_user
from odoo.tests.common import TransactionCase


class TestAuthEmail(TransactionCase):
    """Test the auth_email module."""

    def _create_user(self, login, **kwargs):
        ctx = {
            "mail_create_nolog": True,
            "mail_create_nosubscribe": True,
            "mail_notrack": True,
            "no_reset_password": True,
        }
        user = new_test_user(
            self.env,
            login=login,
            groups="base.group_user",
            context=ctx,
            **kwargs,
        )
        return user

    def _login(self, db, credential, user_agent_env):
        def cursor_exit(exc_type, exc_value, traceback):
            # disable commit/close
            pass

        # patch to force using our test cursor, and avoid closing it, otherwise the
        # newly created user will be not found
        with (
            patch.object(Registry, "cursor", return_value=self.env.cr),
            patch.object(BaseCursor, "__exit__", side_effect=cursor_exit),
        ):
            res_id = self.env["res.users"]._login(db, credential, user_agent_env)
        return res_id

    def setUp(self):
        super().setUp()
        self.test_user = self._create_user("test_auth_email_user")
        self.test_user.email = "user@test_auth_email_user.com"

    def test_01_login(self):
        """Verify that email login is also working."""
        credentials = {
            "type": "password",
            "login": "test_auth_email_user",
            "password": "test_auth_email_user",
        }
        # try classic login using ... login
        res_id = self._login(self.env.cr.dbname, credentials, {"interactive": True})
        self.assertEqual(self.test_user.id, res_id.get("uid"))
        # now try to login using the email instead of the login
        credentials["login"] = "user@test_auth_email_user.com"
        res_id = self._login(self.env.cr.dbname, credentials, {"interactive": True})
        self.assertEqual(self.test_user.id, res_id.get("uid"))

    def test_02_login_case(self):
        alternate_user = self._create_user(
            "test_auth_email_alternate_user",
            email="ALTERNATE_USER@test_auth_email_user.COM",
        )
        self.assertEqual(
            alternate_user.email, "alternate_user@test_auth_email_user.com"
        )
        credentials = {
            "type": "password",
            "login": "ALTERNATE_USER@test_auth_email_user.COM",
            "password": "test_auth_email_alternate_user",
        }
        res_id = self._login(self.env.cr.dbname, credentials, {"interactive": True})
        self.assertEqual(alternate_user.id, res_id.get("uid"))
        # retry with lowercase
        credentials = {
            "type": "password",
            "login": "alternate_user@test_auth_email_user.com",
            "password": "test_auth_email_alternate_user",
        }
        res_id = self._login(self.env.cr.dbname, credentials, {"interactive": True})
        self.assertEqual(alternate_user.id, res_id.get("uid"))
        # change email to uppercase version and retry
        alternate_user.email = "ALTERNATE_USER2@TEST_AUTH_EMAIL_USER.COM"
        credentials["login"] = "alternate_user2@test_auth_email_user.com"
        res_id = self._login(self.env.cr.dbname, credentials, {"interactive": True})
        self.assertEqual(alternate_user.id, res_id.get("uid"))
