# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Dec 2024

import json
import os
import time
from datetime import datetime
from unittest.mock import patch

import odoo.tests
from odoo import http
from odoo.tests import TEST_CURSOR_COOKIE_NAME, Opener, new_test_user
from odoo.tools._vendor.sessions import FilesystemSessionStore


class TestBasePermanentSessionCommon(odoo.tests.HttpCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        # keep original method for future calls
        save_origin = FilesystemSessionStore.save

        # method that will replace the existing one
        def _FilesystemSessionStore_save(self, session):
            # call original method (no return)
            save_origin(self, session)
            # override
            fn = self.get_session_filename(session.sid)
            now = datetime.today()
            modification_time = time.mktime(now.timetuple())
            access_time = modification_time
            os.utime(fn, (access_time, modification_time))

        # prepare mock patch
        cls.patcher = patch.object(
            FilesystemSessionStore,
            "save",
            autospec=True,
            wraps=FilesystemSessionStore,
            side_effect=_FilesystemSessionStore_save,
        )
        # process mock patch
        _r = cls.patcher.start()

    @classmethod
    def tearDownClass(cls):
        # revert mock patch
        cls.patcher.stop()
        super().tearDownClass()

    def setUp(self):
        super().setUp()
        self.users = [
            self._create_user("userA", "userA"),  # 0
            self._create_user("userB", "userB"),  # 1
            self._create_user("userC", "userC"),  # 2
            self._create_user("userD", "userD"),  # 3
            self._create_user("userE", "userE"),  # 4
            self._create_user("userF", "userF"),  # 5
            self._create_user("userG", "userG"),  # 6
            self._create_user("userH", "userH"),  # 7
        ]

    def _create_user(self, login, password):
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
        )
        user.password = password
        return user, login, password

    def _authenticate(self, user_index=0, headers=None):
        # reset request session to ensure cookies are cleared like it is already
        # done in `HttpCaseCommon.setUp()` BUT use Opener instead of requests.Session
        self.opener = Opener(self.cr)
        self.opener.cookies[TEST_CURSOR_COOKIE_NAME] = self.http_request_key
        if not headers:
            headers = {}
        url = "/web/session/authenticate"
        login = self.users[user_index][1]
        password = self.users[user_index][2]
        params = {
            "db": self.env.cr.dbname,
            "login": login,
            "password": password,
        }
        data = {
            "jsonrpc": "2.0",
            "method": "call",
            "params": params,
            "id": 1,
        }
        headers.update(
            {
                "Content-Type": "application/json",
            }
        )
        response = self.url_open(
            url, data=json.dumps(data), headers=headers, timeout=600
        )
        self.assertEqual(response.status_code, 200)
        _result = json.loads(response.text)["result"]
        sid = response.cookies.get("session_id")
        # extract werkzeug session
        session = http.root.session_store.get(sid)
        return session
