# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Apr 2024

import json
from datetime import datetime

from dateutil.relativedelta import relativedelta
from freezegun import freeze_time

import odoo.tests
from odoo import fields
from odoo.tests import new_test_user
from odoo.addons.software_license_portal.controllers.main import SUCCESS, ERROR


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

    def partner_authenticate(self, partner_id, new_password):
        user_id = partner_id.user_ids and partner_id.user_ids[0] or False
        if not user_id:
            self._give_portal_access(partner_id)
        user_id = partner_id.user_ids and partner_id.user_ids[0] or False
        # override password
        user_id.password = new_password
        return self.authenticate(user_id.email, new_password)

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
        # validate hardware "device_uuid_1" using serial "0DAY-0001" on "???"
        res = self._api_validate(6666, "0DAY-0001", "device_uuid_1", payload)
        self.assertEqual(res.get("message_id"), "LICENSE_NOT_FOUND")
        # deactivate hardware "device_uuid_1" using serial "0DAY-0001" on "???"
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

    def test_06_get_serial(self):
        self.authenticate("test-portal", "test-portal")
        res = self._api_get_serial(1001, "6a:32:bb:7f:36:14")
        self.assertEqual(res.get("serial"), "0DAY-0001")
        res = self._api_get_serial(999, "6a:32:bb:7f:36:14")
        self.assertEqual(res.get("serial"), False)
        res = self._api_get_serial(1001, "00:00:00")
        self.assertEqual(res.get("serial"), False)

    def test_07_empty_get_licenses(self):
        self.authenticate("test-portal", "test-portal")
        # test-portal user do not own any license
        res1 = self._api_get_licenses_per_hardware("6a:32:bb:7f:36:14")
        self.assertFalse(res1)
        res2 = self._api_get_licenses_per_identifier(1001)
        self.assertFalse(res2)

    def test_08_get_licenses_per_hardware(self):
        # like test_07 but retry as Brandon Freeman from Azure Interior
        partner_id = self.env.ref("base.res_partner_address_15")
        self.partner_authenticate(partner_id, "password")
        # get per hardware
        res = self._api_get_licenses_per_hardware("6a:32:bb:7f:36:14")
        self.assertEqual(len(res), 1)
        self.assertIn("0DAY-0001", res)
        # check license data content
        licdata = res["0DAY-0001"]
        self.assert_license_data_0DAY0001(licdata)
        # check hardware data content
        self.assertIn("hardwares", licdata)
        hwdata = licdata.pop("hardwares")
        self.assert_hardware_data(hwdata, "6a:32:bb:7f:36:14")

    def test_09_get_licenses_per_identifier(self):
        # like test_07 but retry as Brandon Freeman from Azure Interior
        partner_id = self.env.ref("base.res_partner_address_15")
        self.partner_authenticate(partner_id, "password")
        # get per identifier
        res = self._api_get_licenses_per_identifier(1001)
        self.assertIn("0DAY-0001", res)
        # check license data content
        licdata = res["0DAY-0001"]
        self.assert_license_data_0DAY0001(licdata)
        # check no hardware data
        self.assertNotIn("hardwares", licdata)

    def test_10_get_licenses_per_hardware_wildcard(self):
        hardwares_per_serial = {
            # owned by Azure Interior, Brandon Freeman
            "0DAY-0001": [
                "6a:32:bb:7f:36:14",
                "13:bd:17:6b:03:46",
            ],
            # owned by Azure Interior, Nicole Ford
            "BG-A02": [
                "c5:28:79:ac:8d:b1",
                "72:e8:a5:64:1c:33",
                "6a:05:82:81:94:3c",
                "8b:5e:56:27:6f:8e",
            ],
            # owned by Azure Interior, Brandon Freeman
            "BG-A03": [
                "0d:cc:49:c5:10:86",
            ],
        }
        # try as Brandon Freeman from Azure Interior
        partner_id = self.env.ref("base.res_partner_address_15")
        self.partner_authenticate(partner_id, "password")
        # use wildcard
        res = self._api_get_licenses_per_hardware("*")
        self.assert_hardwares_per_serial_data(
            res,
            hardwares_per_serial,
        )
        # try as Nicole Ford from Azure Interior
        partner_id = self.env.ref("base.res_partner_address_16")
        self.partner_authenticate(partner_id, "password")
        # use wildcard
        res = self._api_get_licenses_per_hardware("*")
        self.assert_hardwares_per_serial_data(
            res,
            hardwares_per_serial,
        )
        # try as Azure Interior
        partner_id = self.env.ref("base.res_partner_12")
        self.partner_authenticate(partner_id, "password")
        # use wildcard
        res = self._api_get_licenses_per_hardware("*")
        self.assert_hardwares_per_serial_data(
            res,
            hardwares_per_serial,
        )

    def test_11_get_licenses_per_hardware_wildcard(self):
        hardwares_per_serial = {
            # owned by Azure Interior
            "N1W9F-6U49E-RW9TL-443F4": [
                "device_uuid_1",
            ],
        }
        # same than test_10 but also include licences from active pass
        pass_basic1 = self.env.ref("software_license_pass.pass_basic1")
        # force pass state owned by Azure Interior
        pass_basic1.state = "sent"
        newage_lic = pass_basic1.license_ids[0]
        self._api_activate(
            newage_lic.application_id.identifier,
            pass_basic1.serial,
            "device_uuid_1",
            self._get_common_payload_with_telemetry(),
        )
        # try as Azure Interior
        partner_id = self.env.ref("base.res_partner_12")
        self.partner_authenticate(partner_id, "password")
        # use wildcard
        res = self._api_get_licenses_per_hardware("*")
        self.assert_hardwares_per_serial_data(
            res,
            hardwares_per_serial,
        )
        # try as Brandon Freeman from Azure Interior
        partner_id = self.env.ref("base.res_partner_address_15")
        self.partner_authenticate(partner_id, "password")
        # use wildcard
        res = self._api_get_licenses_per_hardware("*")
        self.assert_hardwares_per_serial_data(
            res,
            hardwares_per_serial,
        )

    def test_12_get_all_licenses(self):
        # try as Brandon Freeman from Azure Interior
        partner_id = self.env.ref("base.res_partner_address_15")
        self.partner_authenticate(partner_id, "password")
        res = self._api_get_licenses()
        self.assertIn("0DAY-0001", res)
        self.assertIn("BG-A02", res)
        self.assertIn("BG-A03", res)

    def test_13_get_request_info(self):
        res = self._api_get_request_info()
        self.assertIn("telemetry", res)
        self.assertIn("httprequest", res)
        self.assertIn("remote_addr", res["httprequest"])
        self.assertEqual(res["httprequest"]["remote_addr"], "127.0.0.1")

    def test_14_batch_activate_validate_deactivate(self):
        pass_prm3 = self.env.ref("software_license_pass.pass_premium3")
        # force pass state owned by Azure Interior
        pass_prm3.state = "sent"
        # store automatically generated license serial
        lic_serial1 = pass_prm3.license_ids.filtered(
            lambda lic: lic.application_id
            == self.env.ref("software_application.sa_newage")
        ).serial
        lic_serial2 = pass_prm3.license_ids.filtered(
            lambda lic: lic.application_id
            == self.env.ref("software_application.sa_calm")
        ).serial
        lic_serial3 = pass_prm3.license_ids.filtered(
            lambda lic: lic.application_id
            == self.env.ref("software_application.sa_myfitnessapp")
        ).serial
        payload = self._get_common_payload_with_telemetry()
        # use pass serial only (license serials cannot be used for AVD)
        payload["params"]["data"] = {
            "1000": "9NENW-Y2XZT-3GA9C-0CD61",  # New Age
            "1001": "9NENW-Y2XZT-3GA9C-0CD61",  # MyFitnessApp
            "2000": "9NENW-Y2XZT-3GA9C-0CD61",  # Calm
        }
        # activate fake device
        res = self._api_batch_activate("device_uuid_1", payload)
        self.assertIn("9NENW-Y2XZT-3GA9C-0CD61", res)
        actdata = res["9NENW-Y2XZT-3GA9C-0CD61"]
        self.assert_batch_av_result(
            actdata, "1000", SUCCESS, "SERIAL_ACTIVATED_ON_HARDWARE"
        )
        self.assert_batch_av_result(
            actdata, "1001", SUCCESS, "SERIAL_ACTIVATED_ON_HARDWARE"
        )
        self.assert_batch_av_result(
            actdata, "2000", SUCCESS, "SERIAL_ACTIVATED_ON_HARDWARE"
        )
        # get licenses (without login)
        res = self._api_get_licenses_per_hardware("device_uuid_1")
        self.assertIsNone(res)
        # get licenses as Ready Mat
        partner_id = self.env.ref("base.res_partner_4")
        self.partner_authenticate(partner_id, "password")
        res = self._api_get_licenses_per_hardware("device_uuid_1")
        self.assertIn(lic_serial1, res)
        self.assert_license_data(
            res[lic_serial1],
            application_identifier=1000,
            application_name="New Age",
            partner="Ready Mat",
            serial="9NENW-Y2XZT-3GA9C-0CD61",
            remaining_activation=7,
            pass_remaining_activation=7,
            pack="Premium",
            pass_name=pass_prm3.name,
        )
        self.assertIn(lic_serial2, res)
        self.assert_license_data(
            res[lic_serial2],
            application_identifier=2000,
            application_name="Calm",
            partner="Ready Mat",
            serial="9NENW-Y2XZT-3GA9C-0CD61",
            remaining_activation=7,
            pass_remaining_activation=7,
            pack="Premium",
            pass_name=pass_prm3.name,
        )
        self.assertIn(lic_serial3, res)
        self.assert_license_data(
            res[lic_serial3],
            application_identifier=1001,
            application_name="MyFitnessApp",
            partner="Ready Mat",
            serial="9NENW-Y2XZT-3GA9C-0CD61",
            remaining_activation=7,
            pass_remaining_activation=7,
            pack="Premium",
            pass_name=pass_prm3.name,
        )
        # activate another fake devices
        res = self._api_batch_activate("device_uuid_2", payload)
        res = self._api_batch_activate("device_uuid_3", payload)
        # validate first device
        res = self._api_batch_validate("device_uuid_1", payload)
        self.assertIn("9NENW-Y2XZT-3GA9C-0CD61", res)
        valdata = res["9NENW-Y2XZT-3GA9C-0CD61"]
        self.assert_batch_av_result(
            valdata, "1000", SUCCESS, "SERIAL_UPDATED_ON_HARDWARE"
        )
        self.assert_batch_av_result(
            valdata, "1001", SUCCESS, "SERIAL_UPDATED_ON_HARDWARE"
        )
        self.assert_batch_av_result(
            valdata, "2000", SUCCESS, "SERIAL_UPDATED_ON_HARDWARE"
        )
        # get licenses as Ready Mat
        res = self._api_get_licenses_per_hardware("device_uuid_1")
        self.assert_license_data(
            res[lic_serial1],
            remaining_activation=5,
            pass_remaining_activation=5,
        )
        self.assert_license_data(
            res[lic_serial2],
            remaining_activation=5,
            pass_remaining_activation=5,
        )
        self.assert_license_data(
            res[lic_serial3],
            remaining_activation=5,
            pass_remaining_activation=5,
        )
        # deactivate first device (no payload needed)
        res = self._api_batch_deactivate("device_uuid_1", payload={})
        self.assertEqual(res["result"], SUCCESS)
        self.assertEqual(res["message_id"], "ALL_SERIALS_DEACTIVATED_ON_HARDWARE")
        # deactivate unknown device (no payload needed)
        res = self._api_batch_deactivate("device_uuid_unknown", payload={})
        self.assertEqual(res["result"], ERROR)
        self.assertEqual(res["message_id"], "HARDWARE_NOT_FOUND")
