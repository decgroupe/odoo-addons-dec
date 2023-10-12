# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Oct 2023

from unittest.mock import patch

import requests

import odoo.exceptions
from odoo.tests.common import TransactionCase


class TestBaseHealthchecks(TransactionCase):
    def setUp(self):
        super().setUp()
        self.server_action = self.env["ir.actions.server"].create(
            {
                "name": "My Server Action",
                "model_id": self.env.ref("base.model_res_users").id,
                "state": "code",
                "code": "if record: record.write({'data': 'New Name'})",
            }
        )

    def test_01_simple_ping(self):
        url = "https://ping.mydomain.com/token/123456"
        self.server_action.ping_url = url
        with patch(
            "odoo.addons.base_healthchecks.models.healthchecks_ping" ".requests.post"
        ) as post:
            post.return_value = None
            self.server_action.run()
            # check that only two calls have been made
            self.assertEqual(len(post.mock_calls), 2)
            # check first call is start
            self.assertEqual(post.mock_calls[0].args[0], url + "/start")
            # check second call is ping
            self.assertEqual(post.mock_calls[1].args[0], url)

    def test_02_action_exception(self):
        url = "https://ping.mydomain.com/token/123456"
        self.server_action.ping_url = url
        self.server_action.code = "raise Warning('Fake Error')"
        with patch(
            "odoo.addons.base_healthchecks.models.healthchecks_ping" ".requests.post"
        ) as post:
            post.return_value = None
            try:
                self.server_action.run()
            except odoo.exceptions.Warning as e:
                pass
            # check that only two calls have been made
            self.assertEqual(len(post.mock_calls), 2)
            # check first call is start
            self.assertEqual(post.mock_calls[0].args[0], url + "/start")
            # check second call is fail
            self.assertEqual(post.mock_calls[1].args[0], url + "/fail")

    def test_03_action_ping_config_url(self):
        ICP = self.env["ir.config_parameter"].sudo()
        url = ICP.get_param("healthchecks.url")
        cron = self.env.ref("base_healthchecks.ir_cron_healthchecks")
        with patch(
            "odoo.addons.base_healthchecks.models.healthchecks_ping" ".requests.post"
        ) as post:
            post.return_value = None
            cron.method_direct_trigger()
            # check that only one calls have been made
            self.assertEqual(len(post.mock_calls), 1)
            # check call is simple ping
            self.assertEqual(post.mock_calls[0].args[0], url)

    def test_04_ping_log(self):
        url = "https://ping.mydomain.com/token/123456"
        self.server_action.ping_url = url
        self.server_action.code = "ping_log('Custom message')"
        with patch(
            "odoo.addons.base_healthchecks.models.healthchecks_ping" ".requests.post"
        ) as post:
            post.return_value = None
            try:
                self.server_action.run()
            except odoo.exceptions.Warning as e:
                pass
            # check that exactly three calls have been made
            self.assertEqual(len(post.mock_calls), 3)
            # check first call is start
            self.assertEqual(post.mock_calls[0].args[0], url + "/start")
            # check second call is log
            self.assertEqual(post.mock_calls[1].args[0], url + "/log")
            self.assertEqual(
                post.mock_calls[1].kwargs["json"].get("log"), "Custom message"
            )
            # check last call is ping
            self.assertEqual(post.mock_calls[2].args[0], url)

    def test_05_post_fail(self):
        url = "https://ping.mydomain.com/token/123456"
        self.server_action.ping_url = url
        with patch(
            "odoo.addons.base_healthchecks.models.healthchecks_ping" ".requests.post"
        ) as post:
            post.side_effect = requests.HTTPError("Fake HTTP Error")
            post.return_value = None
            self.server_action.run()
            # check that only two calls have been made
            self.assertEqual(len(post.mock_calls), 2)
            # check first call is start
            self.assertEqual(post.mock_calls[0].args[0], url + "/start")
            # check second call is ping
            self.assertEqual(post.mock_calls[1].args[0], url)
