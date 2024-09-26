# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Jul 2024

import json
import logging
import pprint

from lxml import html

import odoo.tests
from odoo.tests import Form, new_test_user

_logger = logging.getLogger(__name__)

API_KEY = "d5b27d10-3db6-47b4-ab7e-412cd4418f6b"


class TestMrpPortalBase(odoo.tests.HttpCase):

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
            groups="mrp.group_mrp_manager",
            context=ctx,
        )
        self.api_key = self.env["auth.api.key"].create(
            {
                "name": "MyRemoteTool",
                "user_id": self.api_user.id,
                "key": API_KEY,
            }
        )
        self.product_model = self.env["product.product"]
        self.p1 = self.product_model.create(
            {
                "name": "101",
                "type": "product",
            }
        )
        self.stock_product = self.product_model.create(
            {
                "name": "Stockable Product",
                "type": "product",
            }
        )
        # Create bill of materials
        self.bom_model = self.env["mrp.bom"]
        self.bom = self.bom_model.create(
            {
                "product_tmpl_id": self.p1.product_tmpl_id.id,
                "product_id": self.p1.id,
                "product_qty": 1,
                "type": "normal",
            }
        )
        # Add at least one stock product or Odoo will complain about adding
        # raw materials
        self.bom_line_model = self.env["mrp.bom.line"]
        self.bom_line_model.create(
            {
                "bom_id": self.bom.id,
                "product_id": self.stock_product.id,
                "product_qty": 1,
            }
        )
        self.production_id = self._generate_mo(self.p1, self.bom, 1.0)
        self.production_id.name = "MO_123456789"

    def _generate_mo(self, product, bom, qty=1.0):
        mo_form = Form(self.env["mrp.production"])
        mo_form.product_id = product
        mo_form.bom_id = bom
        mo_form.product_qty = qty
        mo = mo_form.save()
        return mo

    def _api_mrp_action(self, identifier, action, payload, headers=False):
        if not headers:
            headers = {}
        headers.update(
            {
                "Content-Type": "application/json",
                "Api-Key": API_KEY,
            }
        )
        resp = self.url_open(
            f"/api/mrp/v1/identifier/{identifier}/{action}",
            data=json.dumps(payload),
            headers=headers,
        )
        self.assertEqual(resp.status_code, 200)
        resp_payload = json.loads(resp.text)
        self.assertEqual(resp_payload.get("jsonrpc"), "2.0")
        res = resp_payload.get("result")
        return res

    def _api_mrp_update_quantity(self, identifier, payload, headers=False):
        return self._api_mrp_action(
            identifier=identifier,
            action="UpdateQuantity",
            payload=payload,
            headers=headers,
        )

    def _api_mrp_notify_done(self, identifier, payload, headers=False):
        return self._api_mrp_action(
            identifier=identifier,
            action="NotifyDone",
            payload=payload,
            headers=headers,
        )

    def _api_mrp_notify_cancel(self, identifier, payload, headers=False):
        return self._api_mrp_action(
            identifier=identifier,
            action="NotifyCancel",
            payload=payload,
            headers=headers,
        )

    def assertChecksumInvalid(self, res):
        _logger.debug(pprint.pformat(res))
        self.assertEqual(res["result"], 1)
        self.assertEqual(res["message_id"], "MRP_IDENTIFIER_CHECKSUM_INVALID")
        self.assertEqual(res["message"], "invalid checksum.")
        self.assertIn("computed_checksum", res)
        self.assertNotIn("production_id", res)

    def assertOrderNotFound(self, res):
        _logger.debug(pprint.pformat(res))
        self.assertEqual(res["result"], 1)
        self.assertEqual(res["message_id"], "MRP_ORDER_NOT_FOUND")
        self.assertEqual(res["message"], "no existing production order found.")
        self.assertNotIn("production_id", res)

    def assertOrderNotReady(self, res, production_id, state):
        _logger.debug(pprint.pformat(res))
        self.assertEqual(res["result"], 1)
        self.assertEqual(res["message_id"], "MRP_ORDER_NOT_READY")
        self.assertEqual(res["message"], "production order not ready.")
        self.assertEqual(res["production_id"], production_id.id)
        self.assertEqual(res["state"], state)

    def assertOrderQuantityUpdated(self, res, production_id, state):
        _logger.debug(pprint.pformat(res))
        self.assertEqual(res["result"], 0)
        self.assertEqual(res["message_id"], "MRP_ORDER_QUANTITY_UPDATED")
        self.assertEqual(res["message"], "quantity has been updated.")
        self.assertEqual(res["production_id"], production_id.id)
        self.assertEqual(res["state"], state)

    def assertOrderNotificationCreated(self, res, production_id, state):
        _logger.debug(pprint.pformat(res))
        self.assertEqual(res["result"], 0)
        self.assertEqual(res["message_id"], "MRP_NOTIFICATION_CREATED")
        self.assertEqual(res["message"], "a notification has been created.")
        self.assertEqual(res["production_id"], production_id.id)
        self.assertEqual(res["state"], state)

    def assertProductionAutoActivity(self, activity_id):
        self.assertTrue(activity_id)
        self.assertEqual(len(activity_id), 1)
        self.assertRegex(activity_id.note, "Auto: To Process")
