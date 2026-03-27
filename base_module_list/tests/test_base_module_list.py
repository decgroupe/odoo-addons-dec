# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Mar 2026

import json
import logging

import odoo.tests
from odoo.tests.common import get_db_name

from odoo.addons.base_module_list.controllers.main import URL_MODULES

_logger = logging.getLogger(__name__)


@odoo.tests.tagged("post_install", "-at_install")
class TestBaseModuleList(odoo.tests.HttpCase):
    """Tests for base_module_list HTTP controller."""

    def _call_api(self, dbname=None, headers=None):
        """Post a JSON-RPC request to the installed-modules endpoint and return the
        result."""
        if dbname is None:
            dbname = get_db_name()
        if headers is None:
            headers = {}
        headers.update({"Content-Type": "application/json"})
        payload = {
            "jsonrpc": "2.0",
            "method": "call",
            "params": {"dbname": dbname},
        }
        resp = self.url_open(
            URL_MODULES,
            data=json.dumps(payload),
            headers=headers,
        )
        self.assertEqual(resp.status_code, 200)
        resp_payload = json.loads(resp.text)
        self.assertEqual(resp_payload.get("jsonrpc"), "2.0")
        if "error" in resp_payload:
            message = resp_payload["error"]["data"].get("message")
            debug = resp_payload["error"]["data"].get("debug")
            _logger.error("API Error:\n%s\n%s", message, debug)
        return resp_payload.get("result")

    def test_01_returns_server_wide_modules(self):
        """The '*' key must contain the list of server-wide modules."""
        res = self._call_api()
        self.assertIn("*", res)
        self.assertIsInstance(res["*"], list)

    def test_02_returns_installed_modules_for_db(self):
        """The db key must contain a sorted list of installed module names."""
        dbname = get_db_name()
        res = self._call_api(dbname=dbname)
        self.assertIn(dbname, res)
        modules = res[dbname]
        self.assertIsInstance(modules, list)
        # base is always installed
        self.assertIn("base", modules)
        # base_module_list itself must be installed
        self.assertIn("base_module_list", modules)
        # list must be sorted
        self.assertEqual(modules, sorted(modules))

    def test_03_missing_dbname_raises_error(self):
        """Omitting dbname should return a JSON-RPC error (registry lookup fails)."""
        payload = {
            "jsonrpc": "2.0",
            "method": "call",
            "params": {},
        }
        resp = self.url_open(
            URL_MODULES,
            data=json.dumps(payload),
            headers={"Content-Type": "application/json"},
        )
        self.assertEqual(resp.status_code, 200)
        resp_payload = json.loads(resp.text)
        # None dbname → Registry(None) raises, so we expect an error
        self.assertIn("error", resp_payload)
