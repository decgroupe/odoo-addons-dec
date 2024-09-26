# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Jul 2024

from urllib.parse import quote_plus

import odoo.tests

from .common import TestMrpPortalBase
from ..models.mrp_production import _checksum


@odoo.tests.tagged("post_install", "-at_install")
class TestMrpPortal(TestMrpPortalBase):

    def setUp(self):
        super().setUp()

    def _get_common_payload(self, params):
        return {
            "jsonrpc": "2.0",
            "params": params,
        }

    def test_01_update_production_quantity(self):
        self.production_id.action_confirm()
        self.assertEqual(self.production_id.qty_producing, 0.0)
        payload = self._get_common_payload({"value": 10.0})
        res = self._api_mrp_update_quantity(quote_plus("123456789"), payload)
        self.production_id.invalidate_cache()
        self.assertOrderQuantityUpdated(res, self.production_id, "to_close")
        self.assertEqual(self.production_id.qty_producing, 10.0)

    def test_02_notify_done(self):
        self.production_id.action_confirm()
        payload = self._get_common_payload({})
        res = self._api_mrp_notify_done(quote_plus("123456789"), payload)
        self.production_id.invalidate_cache()
        self.assertOrderNotificationCreated(res, self.production_id, "confirmed")
        self.assertProductionAutoActivity(self.production_id.activity_ids)

    def test_03_notify_cancel(self):
        self.production_id.action_confirm()
        payload = self._get_common_payload({})
        res = self._api_mrp_notify_cancel(quote_plus("123456789"), payload)
        self.production_id.invalidate_cache()
        self.assertOrderNotificationCreated(res, self.production_id, "confirmed")
        self.assertProductionAutoActivity(self.production_id.activity_ids)

    def test_04_update_production_quantity_over_states(self):
        payload = self._get_common_payload({"value": 10.0})
        res = self._api_mrp_update_quantity(quote_plus("0001"), payload)
        self.assertOrderNotFound(res)
        # manually create a new order
        alt_production_id = self._generate_mo(self.p1, self.bom, 50.0)
        alt_production_id.name = "MO_0001"
        self.assertEqual(alt_production_id.qty_producing, 0.0)
        res = self._api_mrp_update_quantity(quote_plus("0001"), payload)
        self.assertOrderNotReady(res, alt_production_id, "draft")
        # confirm order
        self.assertEqual(alt_production_id.qty_producing, 0.0)
        alt_production_id.action_confirm()
        self.assertEqual(alt_production_id.state, "confirmed")
        # update quantity 10/50
        res = self._api_mrp_update_quantity(quote_plus("0001"), payload)
        alt_production_id.invalidate_cache()
        self.assertEqual(alt_production_id.qty_producing, 10.0)
        self.assertOrderQuantityUpdated(res, alt_production_id, "progress")
        # update quantity 50/50
        payload = self._get_common_payload({"value": 50.0})
        res = self._api_mrp_update_quantity(quote_plus("0001"), payload)
        alt_production_id.invalidate_cache()
        self.assertEqual(alt_production_id.qty_producing, 50.0)
        self.assertOrderQuantityUpdated(res, alt_production_id, "to_close")
        # mark as done (force consumed product)
        alt_production_id.move_raw_ids.write({"quantity_done": 1.0})
        action = alt_production_id.with_context(
            skip_consumption=True
        ).button_mark_done()
        self.assertEqual(alt_production_id.state, "done")
        # update quantity 45/50
        payload = self._get_common_payload({"value": 45.0})
        res = self._api_mrp_update_quantity(quote_plus("0001"), payload)
        alt_production_id.invalidate_cache()
        self.assertEqual(alt_production_id.qty_producing, 50.0)
        self.assertOrderNotReady(res, alt_production_id, "done")

    def test_05_notify_over_states(self):
        payload = self._get_common_payload({})
        res = self._api_mrp_notify_done(quote_plus("0001"), payload)
        self.assertOrderNotFound(res)
        res = self._api_mrp_notify_cancel(quote_plus("0001"), payload)
        self.assertOrderNotFound(res)
        # manually create a new order
        alt_production_id = self._generate_mo(self.p1, self.bom, 50.0)
        alt_production_id.name = "MO_0001"
        self.assertEqual(alt_production_id.qty_producing, 0.0)
        res = self._api_mrp_notify_done(quote_plus("0001"), payload)
        self.assertOrderNotReady(res, alt_production_id, "draft")
        res = self._api_mrp_notify_cancel(quote_plus("0001"), payload)
        self.assertOrderNotReady(res, alt_production_id, "draft")
        # confirm order
        alt_production_id.action_confirm()
        self.assertEqual(alt_production_id.state, "confirmed")
        # update quantity 10/50
        alt_production_id.qty_producing = 10.0
        self.assertFalse(alt_production_id.activity_ids)
        res = self._api_mrp_notify_done(quote_plus("0001"), payload)
        self.assertOrderNotificationCreated(res, alt_production_id, "progress")
        alt_production_id.invalidate_cache()
        self.assertEqual(len(alt_production_id.activity_ids), 1)
        res = self._api_mrp_notify_cancel(quote_plus("0001"), payload)
        self.assertOrderNotificationCreated(res, alt_production_id, "progress")
        alt_production_id.invalidate_cache()
        self.assertEqual(len(alt_production_id.activity_ids), 1)
        # delete previously created activities
        alt_production_id._delete_notify_activities()
        # update quantity 50/50
        alt_production_id.qty_producing = 50.0
        self.assertFalse(alt_production_id.activity_ids)
        res = self._api_mrp_notify_done(quote_plus("0001"), payload)
        self.assertOrderNotificationCreated(res, alt_production_id, "to_close")
        alt_production_id.invalidate_cache()
        self.assertEqual(len(alt_production_id.activity_ids), 1)
        res = self._api_mrp_notify_cancel(quote_plus("0001"), payload)
        self.assertOrderNotificationCreated(res, alt_production_id, "to_close")
        alt_production_id.invalidate_cache()
        self.assertEqual(len(alt_production_id.activity_ids), 1)
        # delete previously created activities
        alt_production_id._delete_notify_activities()
        # mark as done (force consumed product)
        alt_production_id.move_raw_ids.write({"quantity_done": 1.0})
        action = alt_production_id.with_context(
            skip_consumption=True
        ).button_mark_done()
        self.assertEqual(alt_production_id.state, "done")
        self.assertFalse(alt_production_id.activity_ids)
        # notification are now ignored
        res = self._api_mrp_notify_done(quote_plus("0001"), payload)
        self.assertOrderNotReady(res, alt_production_id, "done")
        alt_production_id.invalidate_cache()
        self.assertFalse(alt_production_id.activity_ids)
        res = self._api_mrp_notify_cancel(quote_plus("0001"), payload)
        self.assertOrderNotReady(res, alt_production_id, "done")
        alt_production_id.invalidate_cache()
        self.assertFalse(alt_production_id.activity_ids)

    def test_06_checksum(self):
        self.assertEqual(_checksum(240100), 4)
        self.assertEqual(_checksum(240623), 31)
        self.assertEqual(_checksum(240999), 63)
        payload = self._get_common_payload({"checksum":233})
        res = self._api_mrp_notify_done(quote_plus("0001"), payload)
        self.assertChecksumInvalid(res)
        payload = self._get_common_payload({"checksum":1})
        res = self._api_mrp_notify_done(quote_plus("0001"), payload)
        self.assertOrderNotFound(res)

    def test_07_identifier_with_name(self):
        payload = self._get_common_payload({"name":"MO_0001"})
        res = self._api_mrp_notify_done(quote_plus("0001"), payload)
        self.assertOrderNotFound(res)
        prod1_id = self._generate_mo(self.p1, self.bom, 50.0)
        prod1_id.name = "MO_0001"
        res = self._api_mrp_notify_done(quote_plus("0001"), payload)
        self.assertOrderNotReady(res, prod1_id, "draft")
        prod2_id = self._generate_mo(self.p1, self.bom, 50.0)
        prod2_id.name = "MO_0002"
        res = self._api_mrp_notify_done(quote_plus("0002"), payload)
        self.assertOrderNotFound(res)
        self.assertIn("name", res)
        print(res)

    def test_08_ipaddress_header(self):
        self.production_id.action_confirm()
        payload = self._get_common_payload({})
        res = self._api_mrp_notify_cancel(
            quote_plus("123456789"),
            payload,
            headers={"X_FORWARDED_FOR": "1.1.1.1"},
        )
        self.assertIn("1.1.1.1", self.production_id.message_ids[0].body)
