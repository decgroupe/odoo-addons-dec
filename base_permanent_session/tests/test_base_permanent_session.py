# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Dec 2024


import json
import odoo.tests
from odoo import http
from odoo.http import request

from .common import TestBasePermanentSessionCommon


@odoo.tests.tagged("post_install", "-at_install")
class TestBasePermanentSession(TestBasePermanentSessionCommon, odoo.tests.HttpCase):

    def setUp(self):
        super().setUp()

    def _authenticate(self, headers=None):
        if not headers:
            headers = {}
        url = "/web/session/authenticate"
        params = {
            "db": self.env.cr.dbname,
            "login": self.user_login,
            "password": self.user_password,
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
        response = self.url_open(url, data=json.dumps(data), headers=headers)
        self.assertEqual(response.status_code, 200)
        result = json.loads(response.text)["result"]
        sid = response.cookies.get("session_id")
        # extract werkzeug session
        session = http.root.session_store.get(sid)
        return session

    def test_01_authenticate_standard_session(self):
        session = self._authenticate()
        self.assertFalse(session.permanent)
        for value in ["False", "false", "0", "off"]:
            session = self._authenticate({"X-Odoo-Session-Permanent": value})
            self.assertFalse(session.permanent)
            # cleanup session folder
            http.root.session_store.delete(session)

    def test_02_authenticate_permanent_session(self):
        for value in ["True", "true", "1", "on"]:
            session = self._authenticate({"X-Odoo-Session-Permanent": value})
            self.assertTrue(session.permanent)
            # cleanup session folder
            http.root.session_store.delete(session)
