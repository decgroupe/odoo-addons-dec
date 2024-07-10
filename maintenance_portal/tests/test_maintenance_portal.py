# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Jul 2024

from urllib.parse import quote_plus

import odoo.tests

from .common import TestMaintenancePortalBase


@odoo.tests.tagged("post_install", "-at_install")
class TestMaintenancePortal(TestMaintenancePortalBase):

    def setUp(self):
        super().setUp()

    def assertMaintenanceAutoActivity(self, activity_id):
        self.assertTrue(activity_id)
        self.assertEqual(len(activity_id), 1)
        self.assertRegex(activity_id.note, "Auto: To Process")

    def _get_common_payload(self):
        return {
            "jsonrpc": "2.0",
            "params": {
                "name": "Title of my request",
                "maintenance_type": "corrective",
                "description": "Description of the issue",
            },
        }

    def test_01_create_and_update_request(self):
        query_identifier = "test_01"
        # create
        payload = self._get_common_payload()
        res = self._api_maintenance_request(
            quote_plus("MT-122-11112222"),
            quote_plus(query_identifier),
            payload,
        )
        self.assertGreaterEqual(res.get("request_id"), 1)
        request_id = self.env["maintenance.request"].browse(res.get("request_id"))
        self.assertTrue(request_id.exists())
        self.assertEqual(request_id.name, "Title of my request")
        self.assertEqual(request_id.maintenance_type, "corrective")
        self.assertEqual(request_id.description, "Description of the issue")
        self.assertMaintenanceAutoActivity(request_id.activity_ids)
        # update with same query identifier
        payload["params"]["name"] = "Different title for my request"
        res = self._api_maintenance_request(
            quote_plus("MT-122-11112222"),
            quote_plus(query_identifier),
            payload,
        )
        request_id.invalidate_cache()
        self.assertEqual(res.get("request_id"), request_id.id)
        self.assertEqual(request_id.name, "Different title for my request")
        # another update without changing the payload => ping
        res = self._api_maintenance_request(
            quote_plus("MT-122-11112222"),
            quote_plus(query_identifier),
            payload,
        )
        request_id.invalidate_cache()
        self.assertEqual(res.get("request_id"), request_id.id)
        # update with different query identifier => create
        query_identifier = "test_01b"
        payload["params"]["name"] = "Another different title for my request"
        res = self._api_maintenance_request(
            quote_plus("MT-122-11112222"),
            quote_plus(query_identifier),
            payload,
        )
        self.assertNotEqual(res.get("request_id"), request_id.id)
        new_request_id = self.env["maintenance.request"].browse(res.get("request_id"))
        self.assertGreater(new_request_id.id, request_id.id)
        self.assertEqual(new_request_id.name, "Another different title for my request")

    def test_02_ipaddress_header(self):
        query_identifier = "test_02"
        # create
        payload = self._get_common_payload()
        res = self._api_maintenance_request(
            quote_plus("MT-122-11112222"),
            quote_plus(query_identifier),
            payload,
            headers={"X_FORWARDED_FOR": "1.1.1.1"},
        )
        self.assertGreaterEqual(res.get("request_id"), 1)
        request_id = self.env["maintenance.request"].browse(res.get("request_id"))
        self.assertIn("1.1.1.1", request_id.message_ids[0].description)

    def test_03_invalid_equipment(self):
        query_identifier = "test_03"
        # create
        payload = self._get_common_payload()
        res = self._api_maintenance_request(
            quote_plus("000"),
            quote_plus(query_identifier),
            payload,
        )
        self.assertEqual(res["message_id"], "GENERIC_ERROR")
        self.assertEqual(res["message"], "Equipment with serial 000 not found")
        self.assertFalse(res["request_id"])
