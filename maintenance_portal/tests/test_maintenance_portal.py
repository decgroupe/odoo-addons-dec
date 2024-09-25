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

    def _get_common_payload(self, params):
        return {
            "jsonrpc": "2.0",
            "params": params,
        }

    def _get_create_update_payload(self):
        return self._get_common_payload(
            params={
                "name": "Title of my request",
                "maintenance_type": "corrective",
                "description": "Description of the issue",
            }
        )

    def _get_close_payload(self):
        return self._get_common_payload(
            params={
                "closed_reason": "Sensor removed",
            }
        )

    def test_01_create_update_close_request(self):
        query_identifier = "test_01"
        # create
        payload = self._get_create_update_payload()
        res = self._api_maintenance_request(
            quote_plus("MT-122-11112222"),
            quote_plus(query_identifier),
            payload,
        )
        self.assertEqual(res["message_id"], "REQUEST_CREATED")
        self.assertEqual(res["message"], "a new request has been created.")
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
        self.assertEqual(res["message_id"], "REQUEST_UPDATED")
        self.assertEqual(res["message"], "an existing request has been updated.")
        self.assertEqual(res["request_id"], request_id.id)
        request_id.invalidate_cache()
        self.assertEqual(res.get("request_id"), request_id.id)
        self.assertEqual(request_id.name, "Different title for my request")
        # another update without changing the payload => ping
        res = self._api_maintenance_request(
            quote_plus("MT-122-11112222"),
            quote_plus(query_identifier),
            payload,
        )
        self.assertEqual(res["message_id"], "REQUEST_UPDATED")
        self.assertEqual(res["message"], "an existing request has been updated.")
        self.assertEqual(res["request_id"], request_id.id)
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
        self.assertEqual(res["message_id"], "REQUEST_CREATED")
        self.assertEqual(res["message"], "a new request has been created.")
        self.assertNotEqual(res["request_id"], request_id.id)
        self.assertNotEqual(res.get("request_id"), request_id.id)
        new_request_id = self.env["maintenance.request"].browse(res.get("request_id"))
        self.assertGreater(new_request_id.id, request_id.id)
        self.assertEqual(new_request_id.name, "Another different title for my request")
        # close
        query_identifier = "test_01"
        payload = self._get_close_payload()
        res = self._api_maintenance_close(
            quote_plus("MT-122-11112222"),
            quote_plus(query_identifier),
            payload,
        )
        self.assertEqual(res["message_id"], "REQUEST_CLOSED")
        self.assertEqual(res["message"], "an existing request has been closed.")
        self.assertEqual(res["request_id"], request_id.id)

    def test_02_ipaddress_header(self):
        query_identifier = "test_02"
        # create
        payload = self._get_create_update_payload()
        res = self._api_maintenance_request(
            quote_plus("MT-122-11112222"),
            quote_plus(query_identifier),
            payload,
            headers={"X_FORWARDED_FOR": "1.1.1.1"},
        )
        self.assertGreaterEqual(res.get("request_id"), 1)
        request_id = self.env["maintenance.request"].browse(res.get("request_id"))
        self.assertIn("1.1.1.1", request_id.message_ids[0].body)

    def test_03_invalid_equipment(self):
        query_identifier = "test_03"
        # create
        payload = self._get_create_update_payload()
        res = self._api_maintenance_request(
            quote_plus("000"),
            quote_plus(query_identifier),
            payload,
        )
        self.assertEqual(res["message_id"], "GENERIC_ERROR")
        self.assertEqual(res["message"], "Equipment with serial 000 not found")
        self.assertFalse(res["request_id"])

    def test_04_recreate_activity_on_update(self):
        query_identifier = "test_04"
        # create
        payload = self._get_create_update_payload()
        res = self._api_maintenance_request(
            quote_plus("MT-122-11112222"),
            quote_plus(query_identifier),
            payload,
        )
        request_id = self.env["maintenance.request"].browse(res.get("request_id"))
        self.assertMaintenanceAutoActivity(request_id.activity_ids)
        # delete all activities
        request_id.activity_ids.unlink()
        # another update without changing the payload => ping
        res = self._api_maintenance_request(
            quote_plus("MT-122-11112222"),
            quote_plus(query_identifier),
            payload,
        )
        # ensure activity has been recreated
        self.assertMaintenanceAutoActivity(request_id.activity_ids)

    def test_05_close_without_reason(self):
        query_identifier = "test_05"
        # create
        payload = self._get_create_update_payload()
        res = self._api_maintenance_request(
            quote_plus("MT-122-11112222"),
            quote_plus(query_identifier),
            payload,
        )
        request_id = self.env["maintenance.request"].browse(res.get("request_id"))
        # close
        payload = self._get_close_payload()
        payload["params"].pop("closed_reason")
        res = self._api_maintenance_close(
            quote_plus("MT-122-11112222"),
            quote_plus(query_identifier),
            payload,
        )
        self.assertEqual(res["message_id"], "REQUEST_CLOSED")
        self.assertEqual(res["message"], 'an existing request has been closed.')
        self.assertEqual(res["request_id"], request_id.id)

    def test_06_close_unknown_request(self):
        query_identifier = "test_06"
        payload = self._get_close_payload()
        res = self._api_maintenance_close(
            quote_plus("MT-122-11112222"),
            quote_plus(query_identifier),
            payload,
        )
        self.assertEqual(res["message_id"], "REQUEST_NOT_FOUND")
        self.assertEqual(res["message"], "no existing active request found.")
