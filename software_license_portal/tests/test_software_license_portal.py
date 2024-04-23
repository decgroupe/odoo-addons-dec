# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Apr 2024

import json
from datetime import datetime

from dateutil.relativedelta import relativedelta
from freezegun import freeze_time

import odoo.tests
from odoo import fields
from odoo.tests import new_test_user


class TestSoftwareLicensePortalBase(odoo.tests.HttpCase):
    """Test controllers defined for portal mode.
    This is mostly for basic coverage; we don't go as far as fully validating
    HTML produced by our routes.
    """

    def setUp(self):
        super().setUp()
        ctx = {
            "mail_create_nolog": True,
            "mail_create_nosubscribe": True,
            "mail_notrack": True,
            "no_reset_password": True,
        }
        self.company = self.env.ref("base.main_company")
        self.basic_user = new_test_user(
            self.env,
            login="test-user",
            password="test-user",
            context=ctx,
        )
        self.basic_user.parent_id = self.company.partner_id
        self.portal_user = new_test_user(
            self.env,
            login="test-portal",
            password="test-portal",
            groups="base.group_portal",
            context=ctx,
        )
        self.partner_portal = self.portal_user.partner_id
        # self.partner_portal.parent_id = self.company.partner_id

    def _get_common_payload_with_telemetry(self, device_name=False, domain_name=False):
        system_info = {}
        network_information = {}
        if device_name:
            system_info.update({"deviceName": device_name})
        if device_name:
            network_information.update({"HostName": device_name})
        if domain_name:
            network_information.update({"DomainName": domain_name})
        return {
            "params": {
                "telemetry": {
                    "NetworkInformation": network_information,
                    "SystemInfo": system_info,
                }
            }
        }

    def _api_single_call(self, identifier, serial, hardware, payload, action):
        resp = self.url_open(
            f"/api/license/v1/identifier/{identifier}/serial/{serial}/hardware/{hardware}/{action}",
            data=json.dumps(payload),
            headers={"Content-Type": "application/json"},
        )
        self.assertEqual(resp.status_code, 200)
        resp_payload = json.loads(resp.text)
        self.assertEqual(resp_payload.get("jsonrpc"), "2.0")
        res = resp_payload.get("result")
        return res

    def _api_activate(self, identifier, serial, hardware, payload):
        return self._api_single_call(
            identifier,
            serial,
            hardware,
            payload,
            "Activate",
        )

    def _api_validate(self, identifier, serial, hardware, payload):
        return self._api_single_call(
            identifier,
            serial,
            hardware,
            payload,
            "Validate",
        )

    def _api_deactivate(self, identifier, serial, hardware, payload):
        return self._api_single_call(
            identifier,
            serial,
            hardware,
            payload,
            "Deactivate",
        )


@odoo.tests.tagged("post_install", "-at_install")
class TestSoftwareLicensePortal(TestSoftwareLicensePortalBase):

    def setUp(self):
        super().setUp()

    def test_01_activate_validate_deactivate(self):
        self.authenticate("test-portal", "test-portal")
        payload = self._get_common_payload_with_telemetry()
        # activate hardware "device_uuid_1" using serial "0DAY-0001" on "MyFitnessApp"
        res = self._api_activate(1001, "0DAY-0001", "device_uuid_1", payload)
        self.assertEqual(res.get("message_id"), "SERIAL_ACTIVATED_ON_HARDWARE")
        self.assertIn("# MyFitnessApp License (id: 1001)", res.get("license_string"))
        self.assertEqual(res.get("remaining_activation"), 1)
        # activate hardware "device_uuid_2" using same serial "0DAY-0001"
        res = self._api_activate(1001, "0DAY-0001", "device_uuid_2", payload)
        self.assertEqual(res.get("message_id"), "SERIAL_ACTIVATED_ON_HARDWARE")
        self.assertIn("# MyFitnessApp License (id: 1001)", res.get("license_string"))
        self.assertEqual(res.get("remaining_activation"), 0)
        # try activating hardware "device_uuid_3"
        res = self._api_activate(1001, "0DAY-0001", "device_uuid_3", payload)
        self.assertEqual(res.get("message_id"), "SERIAL_TOO_MANY_ACTIVATION")
        # retry activating hardware "device_uuid_2" (already activated)
        res = self._api_activate(1001, "0DAY-0001", "device_uuid_2", payload)
        self.assertEqual(res.get("message_id"), "SERIAL_ALREADY_ACTIVATED_ON_HARDWARE")
        # validate "device_uuid_1"
        res = self._api_validate(1001, "0DAY-0001", "device_uuid_1", payload)
        self.assertEqual(res.get("message_id"), "SERIAL_UPDATED_ON_HARDWARE")
        self.assertIn("# MyFitnessApp License (id: 1001)", res.get("license_string"))
        self.assertEqual(res.get("remaining_activation"), 0)
        # deactivate "device_uuid_1"
        res = self._api_deactivate(1001, "0DAY-0001", "device_uuid_1", payload)
        self.assertEqual(res.get("message_id"), "SERIAL_DEACTIVATED_ON_HARDWARE")
        # validate "device_uuid_2"
        res = self._api_validate(1001, "0DAY-0001", "device_uuid_2", payload)
        self.assertEqual(res.get("message_id"), "SERIAL_UPDATED_ON_HARDWARE")
        self.assertIn("# MyFitnessApp License (id: 1001)", res.get("license_string"))
        self.assertEqual(res.get("remaining_activation"), 1)
        # deactivate "device_uuid_2"
        res = self._api_deactivate(1001, "0DAY-0001", "device_uuid_2", payload)
        self.assertEqual(res.get("message_id"), "SERIAL_DEACTIVATED_ON_HARDWARE")

    def test_02_avd_invalid_serial(self):
        self.authenticate("test-portal", "test-portal")
        payload = self._get_common_payload_with_telemetry()
        # activate hardware "device_uuid_1" using serial "FAKE-SERIAL" on "MyFitnessApp"
        res = self._api_activate(1001, "FAKE-SERIAL", "device_uuid_1", payload)
        self.assertEqual(res.get("message_id"), "LICENSE_NOT_FOUND")
        # validate hardware "device_uuid_1" using serial "FAKE-SERIAL" on "MyFitnessApp"
        res = self._api_validate(1001, "FAKE-SERIAL", "device_uuid_1", payload)
        self.assertEqual(res.get("message_id"), "LICENSE_NOT_FOUND")
        # deactivate hardware "device_uuid_1" using serial "FAKE-SERIAL" on "MyFitnessApp"
        res = self._api_deactivate(1001, "FAKE-SERIAL", "device_uuid_1", payload)
        self.assertEqual(res.get("message_id"), "LICENSE_NOT_FOUND")

    def test_03_avd_invalid_application_identifier(self):
        self.authenticate("test-portal", "test-portal")
        payload = self._get_common_payload_with_telemetry()
        # activate hardware "device_uuid_1" using serial "0DAY-0001" on "???"
        res = self._api_activate(6666, "0DAY-0001", "device_uuid_1", payload)
        self.assertEqual(res.get("message_id"), "LICENSE_NOT_FOUND")
        # activate hardware "device_uuid_1" using serial "0DAY-0001" on "???"
        res = self._api_validate(6666, "0DAY-0001", "device_uuid_1", payload)
        self.assertEqual(res.get("message_id"), "LICENSE_NOT_FOUND")
        # activate hardware "device_uuid_1" using serial "0DAY-0001" on "???"
        res = self._api_deactivate(6666, "0DAY-0001", "device_uuid_1", payload)
        self.assertEqual(res.get("message_id"), "LICENSE_NOT_FOUND")

    def test_04_validate_deactivate_before_activate(self):
        self.authenticate("test-portal", "test-portal")
        payload = self._get_common_payload_with_telemetry()
        # validate "device_uuid_1" using serial "0DAY-0001" on "MyFitnessApp"
        res = self._api_validate(1001, "0DAY-0001", "device_uuid_1", payload)
        self.assertEqual(res.get("message_id"), "SERIAL_NOT_ACTIVATED_ON_HARDWARE")
        # deactivate "device_uuid_1"
        res = self._api_deactivate(1001, "0DAY-0001", "device_uuid_1", payload)
        self.assertEqual(res.get("message_id"), "SERIAL_NOT_ACTIVATED_ON_HARDWARE")

    def test_05_activate_validate_expired(self):
        self.authenticate("test-portal", "test-portal")
        payload = self._get_common_payload_with_telemetry()
        # change expiration date in the past
        lic1 = self.env.ref("software_license.sl_myfitnessapp1")
        for hardware_id in lic1.hardware_ids:
            hardware_id.validation_date = fields.Datetime.now() - relativedelta(days=8)
        lic1.expiration_date = fields.Datetime.now() - relativedelta(days=7)
        # activate "device_uuid_1" using serial "0DAY-0001" on "MyFitnessApp"
        res = self._api_activate(1001, "0DAY-0001", "device_uuid_1", payload)
        self.assertEqual(res.get("message_id"), "SERIAL_EXPIRED")
        # try validating existing hardware
        self.assertIn("6a:32:bb:7f:36:14", lic1.hardware_ids.mapped("name"))
        res = self._api_validate(1001, "0DAY-0001", "6a:32:bb:7f:36:14", payload)
        self.assertEqual(res.get("message_id"), "SERIAL_EXPIRED")
        # deactivate existing hardware
        res = self._api_deactivate(1001, "0DAY-0001", "6a:32:bb:7f:36:14", payload)
        self.assertEqual(res.get("message_id"), "SERIAL_DEACTIVATED_ON_HARDWARE")
        # try activating unknown hardware
        res = self._api_activate(1001, "0DAY-0001", "abcdef", payload)
        self.assertEqual(res.get("message_id"), "SERIAL_EXPIRED")
        # try validating unknown hardware
        res = self._api_validate(1001, "0DAY-0001", "abcdef", payload)
        self.assertEqual(res.get("message_id"), "SERIAL_EXPIRED")
        # try deactivating unknown hardware
        res = self._api_deactivate(1001, "0DAY-0001", "abcdef", payload)
        self.assertEqual(res.get("message_id"), "SERIAL_NOT_ACTIVATED_ON_HARDWARE")
        print(1)
