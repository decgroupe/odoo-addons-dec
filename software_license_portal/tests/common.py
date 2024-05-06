# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, May 2024

import json

from lxml import html

import odoo.tests
from odoo.tests import new_test_user


class TestSoftwareLicensePortalBase(odoo.tests.HttpCase):

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

    def html_doc(self, response):
        """Get an HTML LXML document."""
        return html.fromstring(response.text)

    def _in_portal(self, user_id):
        return self.env.ref("base.group_portal") in user_id.groups_id

    def _give_portal_access(self, partner_id):
        PortalWizard = self.env["portal.wizard"]
        PortalWizardUser = self.env["portal.wizard.user"]
        wizard_id = PortalWizard.sudo().create({})
        wizard_user_id = PortalWizardUser.sudo().create(
            {
                "wizard_id": wizard_id.id,
                "partner_id": partner_id.id,
                "email": partner_id.email,
                "in_portal": True,
            }
        )
        return wizard_id.action_apply()

    def partner_authenticate(self, partner_id, custom_password=False):
        user_id = partner_id.user_ids and partner_id.user_ids[0] or False
        if not user_id:
            self._give_portal_access(partner_id)
        user_id = partner_id.user_ids and partner_id.user_ids[0] or False
        # override password
        if custom_password:
            user_id.password = custom_password
        else:
            # otherwise use login as password
            user_id.password = user_id.email
        return self.authenticate(user_id.email, custom_password or user_id.email)

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

    def _api_get_serial(self, identifier, hardware):
        resp = self.url_open(
            f"/api/license/v1/identifier/{identifier}/hardware/{hardware}/Serial",
            data=json.dumps({}),
            headers={"Content-Type": "application/json"},
        )
        self.assertEqual(resp.status_code, 200)
        resp_payload = json.loads(resp.text)
        self.assertEqual(resp_payload.get("jsonrpc"), "2.0")
        res = resp_payload.get("result")
        return res

    def _api_get_licenses_per_hardware(self, hardware):
        resp = self.url_open(
            f"/api/license/v1/hardware/{hardware}/Licenses",
            data=json.dumps({}),
            headers={"Content-Type": "application/json"},
        )
        self.assertEqual(resp.status_code, 200)
        resp_payload = json.loads(resp.text)
        self.assertEqual(resp_payload.get("jsonrpc"), "2.0")
        res = resp_payload.get("result")
        return res

    def _api_get_licenses_per_identifier(self, identifier):
        resp = self.url_open(
            f"/api/license/v1/identifier/{identifier}/Licenses",
            data=json.dumps({}),
            headers={"Content-Type": "application/json"},
        )
        self.assertEqual(resp.status_code, 200)
        resp_payload = json.loads(resp.text)
        self.assertEqual(resp_payload.get("jsonrpc"), "2.0")
        res = resp_payload.get("result")
        return res

    def _api_get_licenses(self):
        resp = self.url_open(
            "/api/license/v1/Licenses",
            data=json.dumps({}),
            headers={"Content-Type": "application/json"},
        )
        self.assertEqual(resp.status_code, 200)
        resp_payload = json.loads(resp.text)
        self.assertEqual(resp_payload.get("jsonrpc"), "2.0")
        res = resp_payload.get("result")
        return res

    def _api_action_call(self, identifier, serial, hardware, payload, action):
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
        return self._api_action_call(identifier, serial, hardware, payload, "Activate")

    def _api_validate(self, identifier, serial, hardware, payload):
        return self._api_action_call(identifier, serial, hardware, payload, "Validate")

    def _api_deactivate(self, identifier, serial, hardware, payload):
        return self._api_action_call(
            identifier, serial, hardware, payload, "Deactivate"
        )

    def _api_get_request_info(self):
        resp = self.url_open("/api/license/v1/Infos")
        self.assertEqual(resp.status_code, 200)
        res = json.loads(resp.text)
        return res

    def _api_batch_call(self, hardware, payload, action):
        resp = self.url_open(
            f"/api/license/v1/hardware/{hardware}/{action}",
            data=json.dumps(payload),
            headers={"Content-Type": "application/json"},
        )
        self.assertEqual(resp.status_code, 200)
        resp_payload = json.loads(resp.text)
        self.assertEqual(resp_payload.get("jsonrpc"), "2.0")
        res = resp_payload.get("result")
        return res

    def _api_batch_activate(self, hardware, payload):
        return self._api_batch_call(hardware, payload, "Activate")

    def _api_batch_validate(self, hardware, payload):
        return self._api_batch_call(hardware, payload, "Validate")

    def _api_batch_deactivate(self, hardware, payload):
        return self._api_batch_call(hardware, payload, "Deactivate")

    def assert_license_data(
        self,
        data,
        application_identifier=None,
        application_name=None,
        partner=None,
        serial=None,
        remaining_activation=None,
        pass_remaining_activation=None,
        pack=None,
        pass_name=None,
    ):
        if application_identifier is not None:
            self.assertEqual(data["application_identifier"], application_identifier)
        if application_name is not None:
            self.assertEqual(data["application_name"], application_name)
        if partner is not None:
            self.assertEqual(data["partner"], partner)
        if serial is not None:
            self.assertEqual(data["serial"], serial)
        if remaining_activation is not None:
            self.assertEqual(data["remaining_activation"], remaining_activation)
        if pass_remaining_activation is not None:
            self.assertEqual(
                data["pass_remaining_activation"], pass_remaining_activation
            )
        if pack is not None:
            self.assertEqual(data["pack"], pack)
        if pass_name is not None:
            self.assertEqual(data["pass"], pass_name)

    def assert_license_data_0DAY0001(self, data):
        self.assert_license_data(
            data,
            application_identifier=1001,
            application_name="MyFitnessApp",
            partner="Azure Interior, Brandon Freeman",
            serial="0DAY-0001",
            remaining_activation=2,
            pass_remaining_activation=0,
        )
        self.assertFalse(data["pack"])
        self.assertFalse(data["pass"])
        self.assertIn("features", data)
        self.assertIn("expiration_date", data)

    def assert_hardware_data(self, data, name):
        self.assertIn(name, data)
        self.assertIn("hardware_identifier", data[name])
        self.assertIn("dongle_identifier", data[name])
        self.assertIn("date", data[name])
        self.assertIn("validity_days", data[name])
        self.assertIn("validation_expiration_date", data[name])

    def assert_hardwares_per_serial_data(self, res, hardwares_per_serial):
        for serial, hardwares in hardwares_per_serial.items():
            self.assertIn(serial, res)
            licdata = res[serial]
            self.assertIn("hardwares", licdata)
            hwdata = licdata["hardwares"]
            for hardware in hardwares:
                self.assert_hardware_data(hwdata, hardware)

    def assert_batch_av_result(self, av_data, identifier, result, message_id):
        self.assertIn(identifier, av_data)
        self.assertEqual(av_data[identifier]["result"], result)
        self.assertEqual(av_data[identifier]["message_id"], message_id)
