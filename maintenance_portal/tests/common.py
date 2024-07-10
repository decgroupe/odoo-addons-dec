# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Jul 2024

import json
import logging

from lxml import html

import odoo.tests
from odoo.tests import new_test_user

_logger = logging.getLogger(__name__)

API_KEY = "d5b27d10-3db6-47b4-ab7e-412cd4418f6b"


class TestMaintenancePortalBase(odoo.tests.HttpCase):

    def setUp(self):
        super().setUp()
        ctx = {
            "mail_create_nolog": True,
            "mail_create_nosubscribe": True,
            "mail_notrack": True,
            "no_reset_password": True,
        }
        self.company = self.env.ref("base.main_company")
        self.api_user = new_test_user(
            self.env,
            login="api-user",
            password="api-user",
            groups="maintenance.group_equipment_manager",
            context=ctx,
        )
        self.api_key = self.env["auth.api.key"].create(
            {
                "name": "MyRemoteTool",
                "user_id": self.api_user.id,
                "key": API_KEY,
            }
        )
        # Samsung Monitor 15", serial => MT/122/11112222
        self.equipment_id = self.env.ref("maintenance.equipment_monitor1")
        # replace slashes in serial has it it not supported by werkzeug actually
        self.equipment_id.serial_no = "MT-122-11112222"

    def _api_maintenance_request(self, serial, identifier, payload, headers=False):
        if not headers:
            headers = {}
        headers.update(
            {
                "Content-Type": "application/json",
                "Api-Key": API_KEY,
            }
        )
        resp = self.url_open(
            f"/api/maintenance/v1/serial/{serial}/id/{identifier}/Request",
            data=json.dumps(payload),
            headers=headers,
        )
        self.assertEqual(resp.status_code, 200)
        resp_payload = json.loads(resp.text)
        self.assertEqual(resp_payload.get("jsonrpc"), "2.0")
        res = resp_payload.get("result")
        return res
