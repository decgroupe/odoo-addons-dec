# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Oct 2023


import contextlib
from unittest.mock import Mock

import odoo
from odoo import api
from odoo.exceptions import AccessDenied, UserError
from odoo.service import security
from odoo.tests.common import (
    HOST,
    TEST_CURSOR_COOKIE_NAME,
    ChromeBrowser,
    HttpCase,
    Opener,
    get_db_name,
    new_test_user,
)
from odoo.tools.misc import DotDict


@contextlib.contextmanager
def MockRequest(env, environ=None, remote_addr=False):
    environ = environ or {}
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
        s.callback(odoo.http._request_stack.pop)
        yield request


class TestAuthLocalPassword(HttpCase):
    # pylint: disable=E501
    def authenticate_nopatch(self, user, password, browser: ChromeBrowser = None):
        """Copy from odoo/odoo/tests/common.py:HttpCase.authenticate
        But the patching of _check_credentials is removed to allow testing
        of our custom _check_credentials method.
        """
        # fmt: off
        if getattr(self, 'session', None):
            odoo.http.root.session_store.delete(self.session)

        self.session = session = odoo.http.root.session_store.new()
        session.update(odoo.http.get_default_session(), db=get_db_name())
        session.context['lang'] = odoo.http.DEFAULT_LANG

        if user: # if authenticated
            # Flush and clear the current transaction.  This is useful, because
            # the call below opens a test cursor, which uses a different cache
            # than this transaction.
            self.cr.flush()
            self.cr.clear()

            credential = {'login': user, 'password': password, 'type': 'password'}
            auth_info = self.registry['res.users'].authenticate(session.db, credential, {'interactive': False})  # noqa: E501
            uid = auth_info['uid']
            env = api.Environment(self.cr, uid, {})
            session.uid = uid
            session.login = user
            session.session_token = uid and security.compute_session_token(session, env)
            session.context = dict(env['res.users'].context_get())

        odoo.http.root.session_store.save(session)
        # Reset the opener: turns out when we set cookies['foo'] we're really
        # setting a cookie on domain='' path='/'.
        #
        # But then our friendly neighborhood server might set a cookie for
        # domain='localhost' path='/' (with the same value) which is considered
        # a *different* cookie following ours rather than the same.
        #
        # When we update our cookie, it's done in-place, so the server-set
        # cookie is still present and (as it follows ours and is more precise)
        # very likely to still be used, therefore our session change is ignored.
        #
        # An alternative would be to set the cookie to None (unsetting it
        # completely) or clear-ing session.cookies.
        self.opener = Opener(self.cr)
        self.opener.cookies['session_id'] = session.sid
        self.opener.cookies[TEST_CURSOR_COOKIE_NAME] = self.http_request_key
        if browser:
            self._logger.info('Setting session cookie in browser')
            browser.set_cookie('session_id', session.sid, '/', HOST)
            browser.set_cookie(TEST_CURSOR_COOKIE_NAME, self.http_request_key, '/', HOST)  # noqa: E501

        return session

    def setUp(self):
        super().setUp()
        self.user = new_test_user(
            self.env,
            login="test_user_1",
            groups="auth_local_password.group_local_password",
        )

    def test_01_min_requirement(self):
        ERROR_MSG = "local password does not meet the minimum length"
        with self.assertRaisesRegex(UserError, ERROR_MSG), self.cr.savepoint():
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
        self.authenticate_nopatch("test_user_1", classic_password)
        # test PIN login
        pin_password = "1234"
        self.user.local_password = pin_password
        # an error should be raised if IP address not found
        with self.assertRaisesRegex(AccessDenied, ERROR_MSG), self.cr.savepoint():
            self.authenticate_nopatch("test_user_1", pin_password)
        # test PIN login from local network
        with MockRequest(self.env, environ={"HTTP_X_FORWARDED_FOR": "192.168.10.1"}):
            self.authenticate_nopatch("test_user_1", pin_password)
        with MockRequest(self.env, remote_addr="192.168.10.1"):
            self.authenticate_nopatch("test_user_1", pin_password)
        # test PIN login from internet network
        with self.assertRaisesRegex(AccessDenied, ERROR_MSG), self.cr.savepoint():
            with MockRequest(self.env, environ={"HTTP_X_FORWARDED_FOR": "88.10.20.2"}):
                self.authenticate_nopatch("test_user_1", pin_password)
        with self.assertRaisesRegex(AccessDenied, ERROR_MSG), self.cr.savepoint():
            with MockRequest(self.env, remote_addr="88.10.20.2"):
                self.authenticate_nopatch("test_user_1", pin_password)
