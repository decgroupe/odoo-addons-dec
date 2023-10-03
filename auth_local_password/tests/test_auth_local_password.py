# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Oct 2023


import contextlib
from unittest.mock import Mock

import odoo
from odoo.exceptions import UserError, AccessDenied
from odoo.tests.common import HttpCase, SavepointCase, new_test_user
from odoo.tools.misc import DotDict


@contextlib.contextmanager
def MockRequest(env, environ={}, remote_addr=False):
    environ.update({"REMOTE_ADDR": "127.0.0.1"})
    request = Mock(
        db=None,
        env=env,
        httprequest=Mock(
            host="localhost",
            path="/",
            app=odoo.http.root,
            environ=environ,
            cookies={},
            referrer="",
            remote_addr=remote_addr,
        ),
        session=DotDict(
            debug=False,
        ),
    )
    with contextlib.ExitStack() as s:
        odoo.http._request_stack.push(request)
        yield request


class TestAuthLocalPassword(SavepointCase, HttpCase):
    def setUp(self):
        super().setUp()
        self.user = new_test_user(
            self.env,
            login="test_user_1",
            groups="auth_local_password.group_local_password",
        )

    def test_01_min_requirement(self):
        ERROR_MSG = "local password does not meet the minimum length"
        with self.assertRaisesRegex(UserError, ERROR_MSG):
            self.user.local_password = "123"

    def test_02_clear_password(self):
        self.user.local_password = "1234"
        self.user.local_password = False
        self.assertFalse(self.user.local_password)
        self.user.local_password = "1234"
        self.user.local_password = ""
        self.assertFalse(self.user.local_password)

    def test_03_authenticate(self):
        ERROR_MSG = "Cannot use a local password from Internet"
        # test classic login
        classic_password = "AAaa1234!@#$"
        self.user.password = classic_password
        self.authenticate("test_user_1", classic_password)
        # test PIN login
        pin_password = "1234"
        self.user.local_password = pin_password
        # an error should be raised if IP address not found
        with self.assertRaisesRegex(AccessDenied, ERROR_MSG):
            self.authenticate("test_user_1", pin_password)
        # test PIN login from local network
        with MockRequest(self.env, environ={"HTTP_X_FORWARDED_FOR": "192.168.10.1"}):
            self.authenticate("test_user_1", pin_password)
        with MockRequest(self.env, remote_addr="192.168.10.1"):
            self.authenticate("test_user_1", pin_password)
        # test PIN login from internet network
        with self.assertRaisesRegex(AccessDenied, ERROR_MSG):
            with MockRequest(self.env, environ={"HTTP_X_FORWARDED_FOR": "88.10.20.2"}):
                self.authenticate("test_user_1", pin_password)
        with self.assertRaisesRegex(AccessDenied, ERROR_MSG):
            with MockRequest(self.env, remote_addr="88.10.20.2"):
                self.authenticate("test_user_1", pin_password)
